Для обучения:
- Необходимо создать папку data в корне проекта, в ней папку masks.
- в папку masks необходимо поместить исходные бинарные маски торосов

На данном этапе, создана модульная, гибкая система кода, позволяющая без больших усилий внедрять изменения в проект.
Что есть:
- Препроцессор для исходных данных, который приводит сырые входные данные, с помощью ряда процессоров, к нужному формату
- Генератор датасета. На основе аугментаций "раздувает" входные данные.
- Создатель датасета - управляет препроцессингом и генерацией датасета, также позволяет получить готовые DataLoader's для обучения
- Модульная архитектура моделей GAN

  На данный момент, модель не использует предобученные веса, проект разработан на Pytorch, без использования готовых моделей.
  Является учебным проектом. Полностью не завершён.
