---
type: source
source_file: "raw/papers/Krizhevsky-2012.pdf"
sha256: "90137160c57217953d5f61857e64ca58e85f06e1b13b4f475c918b1b582b9771"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-Krizhevsky-2012]]"
tags: [ingested, Krizhevsky-2012, cnn, relu, dropout, imagenet]
---

# Ringkasan Sumber: ImageNet Classification with Deep Convolutional Neural Networks

Makalah ini (biasa dikenal sebagai **AlexNet**) melatih convolutional neural network (CNN) yang besar dan mendalam untuk mengklasifikasikan 1,2 juta gambar resolusi tinggi dalam kontes ImageNet LSVRC-2010 ke dalam 1000 kelas berbeda. Pada data pengujian, model ini mencapai tingkat kesalahan (error rate) top-1 sebesar 37,5% dan top-5 sebesar 17,0%, secara signifikan mengungguli state-of-the-art sebelumnya.

### Kontribusi Utama & Arsitektur
- **ReLU Nonlinearity**: Menggantikan fungsi aktivasi yang jenuh (saturating activation functions seperti tanh, sigmoid) dengan fungsi non-saturating $\max(0, x)$, mempercepat pelatihan hingga enam kali lipat.
- **Multi-GPU Training**: Menyebarkan parameter jaringan dan komputasi pada dua GPU dengan pembatasan komunikasi lintas GPU.
- **Local Response Normalization (LRN)**: Mekanisme lateral inhibition yang membantu generalisasi model.
- **Overlapping Pooling**: Penggunaan jendela pooling yang tumpang tindih untuk mengurangi overfitting.
- **Dropout**: Menyetel output neuron tersembunyi menjadi nol dengan probabilitas 0.5 selama pelatihan untuk mencegah co-adaptation dan overfitting.
- **Data Augmentation**: Mengurangi overfitting melalui translasi gambar, refleksi horizontal, dan penyesuaian intensitas warna RGB berbasis PCA.

## Konsep Inti

- [[deep-convolutional-neural-networks-id]]
- [[relu-nonlinearity-id]]
- [[dropout-regularization-id]]

## Entitas Terkait

- [[alex-krizhevsky-id]]
- [[ilya-sutskever-id]]
- [[geoffrey-hinton-id]]
- [[imagenet-dataset-id]]
- [[cuda-convnet-id]]\n