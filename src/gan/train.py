import os
import torch
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict

from src.gan.model import GenerativeModel
from src.datasets.dataset import DatasetCreator

import os
import torch
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict

from src.gan.model import GenerativeModel
from src.datasets.dataset import DatasetCreator

class GANTrainer:
    def __init__(self, model: GenerativeModel, dataset_processor: DatasetCreator, output_path, 
                 epochs=10, batch_size=10, load_weights=True, early_stop_patience=50):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = model
        self.load_weights = load_weights
        self.dataset_processor = dataset_processor
        self.output_path = output_path
        self.epochs = epochs
        self.batch_size = batch_size
        self.early_stop_patience = early_stop_patience
        
        # Активируем планировщики скорости обучения
        self.g_scheduler = self.model.g_trainer.scheduler
        self.c_scheduler = self.model.c_trainer.scheduler
        
        self.epoch_g_losses = defaultdict(float)
        self.epoch_d_losses = defaultdict(float)
        
        os.makedirs(self.output_path, exist_ok=True)
        
    def train(self):
            train_loader, val_loader = self.dataset_processor.create_dataloaders(
                batch_size=self.batch_size, shuffle=True, workers=4
            )
            
            self.model.generator.train()
            for epoch in range(self.epochs):
                self._epoch_run(train_loader, training=True, epoch=epoch)
                self._epoch_run(val_loader, training=False, epoch=epoch)
                
                self.model.g_metrics.print_average_metrics(epoch=epoch, phase="train")
                self.model.g_metrics.reset_running_stats()
                
                self.model._save_models(self.output_path)

    def _epoch_run(self, loader, training=True, epoch=0):
        for i, batch in enumerate(tqdm(loader, desc=f"Epoch {epoch+1} {'Train' if training else 'Val'}")):
            batch_data = self._process_batch(batch, training)
            
            if not training and i == 0:
                self._visualize_batch(batch_data['inputs'], batch_data['generated'], batch_data['targets'], epoch, 
                                      phase='train' if training else 'val')

    def _process_batch(self, batch, training):
        inputs, targets, masks = [tensor.to(self.device) for tensor in batch]
        
        if training:
            losses = self.model.train_step(inputs, targets, masks)
            self._update_losses(losses)
        
        with torch.no_grad():
            generated = self.model.generator(inputs, masks)

            self.model.g_metrics.calculate_metrics(generated, targets, masks)
            self.model.g_metrics.print_metrics(phase="train")
            
        return {
            'inputs': inputs, 
            'generated': generated, 
            'targets': targets
        }

    def _update_losses(self, losses):
        for key in losses['g_losses']:
            self.epoch_g_losses[key] = self.epoch_g_losses.get(key, 0.0) + losses['g_losses'][key]
        for key in losses['d_losses']:
            self.epoch_d_losses[key] = self.epoch_d_losses.get(key, 0.0) + losses['d_losses'][key]

    def _visualize_batch(self, inputs, generated, targets, epoch, phase='train'):
        plt.figure(figsize=(15, 6))
        for i in range(min(3, inputs.shape[0])):
            plt.subplot(3, 3, i+1)
            plt.imshow(inputs[i].cpu().squeeze(), cmap='gray')
            plt.title(f"Input {i+1}")
            
            plt.subplot(3, 3, i+4)
            plt.imshow(generated[i].cpu().squeeze(), cmap='gray')
            plt.title(f"Generated {i+1}")
            
            plt.subplot(3, 3, i+7)
            plt.imshow(targets[i].cpu().squeeze(), cmap='gray')
            plt.title(f"Target {i+1}")
        
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/{phase}.png")
        plt.close()