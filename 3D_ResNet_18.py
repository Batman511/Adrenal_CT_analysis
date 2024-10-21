import numpy as np
import os
import matplotlib.pyplot as plt
import Data_Prepare


#----------------Загрузка массивов данных----------------#

project_dir = os.path.dirname(os.path.abspath(__file__))

# Определите пути к файлам
videos_file = os.path.join(project_dir, 'videos.npy')
labels_file = os.path.join(project_dir, 'labels.npy')
labels_names_file = os.path.join(project_dir, 'labels_names.npy')

# Загрузка массивов
videos = np.load(videos_file)
labels = np.load(labels_file)
label_names = np.load(labels_names_file)

# Проверка загруженных данных
print(f"Размерность массива видео: {videos.shape}")     # (Число видео, Число кадров, Высота, Ширина, Глубина)
print(f"Размерность одного видео: {videos[0].shape}")   # (Число кадров, Высота, Ширина, Глубина)
print(f"Размерность массива меток: {labels.shape}")


# Построение гистограммы
unique_labels, label_counts = np.unique(label_names, return_counts=True)
colors = ['#FF8C00' if 'left' in label else '#1E90FF' for label in unique_labels]
plt.figure(figsize=(12, 6))
plt.bar(range(len(unique_labels)), label_counts, color=colors, tick_label=unique_labels)
plt.ylabel('Число примеров')
plt.title('Число примеров в классе')
plt.xticks()
plt.tight_layout()
plt.show()


# left_count = np.sum([count for label, count in zip(unique_labels, label_counts) if 'left' in label])
# right_count = np.sum([count for label, count in zip(unique_labels, label_counts) if 'right' in label])
# categories = ['left', 'right']
# counts = [left_count, right_count]
# plt.figure(figsize=(8, 5))
# plt.bar(categories, counts, color=['#FF8C00', '#1E90FF'])  # Оранжевый для left и синий для right
# plt.ylabel('Number of Videos')
# plt.title('Number of Videos: Left vs Right')
# plt.show()
