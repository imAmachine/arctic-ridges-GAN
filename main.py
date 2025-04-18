from src.preprocessing.preprocessor import IceRidgeDatasetPreprocessor
from src.gan.dataset import DatasetCreator, InferenceMaskingProcessor
from src.gan.model import GenerativeModel
from src.gan.train import GANTrainer
from gui import ImageGenerationApp
from settings import *
import argparse
import tkinter as tk


def main():
    parser = argparse.ArgumentParser(description='GAN модель для генерации ледовых торосов')
    parser.add_argument('--preprocess', action='store_true', help='Препроцессинг исходных данных')
    parser.add_argument('--train', action='store_true', help='Обучение модели')
    parser.add_argument('--infer', action='store_true', help='Инференс на одном изображении')
    parser.add_argument('--input_path', type=str, help='Путь к изображению для инференса')
    parser.add_argument('--epochs', type=int, default=20000, help='Количество эпох обучения')
    parser.add_argument('--batch_size', type=int, default=3, help='Размер батча')
    parser.add_argument('--load_weights', action='store_true', help='Загрузить сохраненные веса модели')
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')

    args = parser.parse_args()

    run_all = not (args.preprocess or args.train or args.infer or args.gui)

    # Инициализация модели
    model_gan = GenerativeModel(target_image_size=224, 
                                g_feature_maps=64, 
                                d_feature_maps=32,
                                device=DEVICE,
                                lr=0.0005,
                                n_critic=2,
                                lambda_w=10.0,
                                lambda_bce=10.0,
                                lambda_gp=10.0,
                                lambda_l1=1.5,
                                lambda_bin_enf=0.1)

    # Инициализация создателя датасета
    ds_creator = DatasetCreator(generated_path=AUGMENTED_DATASET_FOLDER_PATH,
                                original_data_path=MASKS_FOLDER_PATH,
                                preprocessed_data_path=PREPROCESSED_MASKS_FOLDER_PATH,
                                images_extentions=MASKS_FILE_EXTENSIONS,
                                model_transforms=model_gan.get_model_transforms(),
                                preprocessors=PREPROCESSORS,
                                augmentations=AUGMENTATIONS,
                                device=DEVICE)

    # Препроцессинг данных
    if args.preprocess or run_all:
        print("Выполняется препроцессинг данных...")
        ds_creator.preprocess_data()

    # Обучение модели
    if args.train or run_all:
        print(f"Запуск обучения модели на {args.epochs} эпох...")
        trainer = GANTrainer(model=model_gan, 
                             dataset_processor=ds_creator,
                             output_path=WEIGHTS_PATH,
                             epochs=args.epochs,
                             device=DEVICE,
                             batch_size=args.batch_size,
                             load_weights=args.load_weights,
                             val_ratio=0.2,
                             checkpoints_ratio=15)
        
        trainer.train()

    # Инференс
    if args.infer:
        if not args.input_path:
            print("Ошибка: для инференса необходимо указать --input_path путь к изображению.")
            return
        img = Utils.cv2_load_image(args.input_path, cv2.IMREAD_GRAYSCALE)
        preprocessor = IceRidgeDatasetPreprocessor(PREPROCESSORS)
        preprocessed_img = preprocessor.process_image(img)
        
        processor = InferenceMaskingProcessor(outpaint_ratio=0.2)
        generated, original = model_gan.infer_generate(preprocessed_img=preprocessed_img, 
                                                       checkpoint_path=WEIGHTS_PATH, 
                                                       processor=processor)

        output_path = 'D:/h/gacha/toros/suka/arctic-ridges-GAN/data/musor/output.png'
        cv2.imwrite(output_path, generated)
        print(f"Генерация завершена. Результат сохранён в {output_path}")

    if args.gui:
        root = tk.Tk()
        app = ImageGenerationApp(root, WEIGHTS_PATH, model_gan, args)
        root.mainloop()
        return
        

if __name__ == "__main__":
    main()
