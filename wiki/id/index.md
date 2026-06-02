# Indeks Wiki

Selamat datang di basis pengetahuan pribadi Anda. Di bawah ini adalah katalog visual dan terkategori otomatis dari semua pengetahuan yang terkompilasi, dikelompokkan berdasarkan **Ranah/Domain** terlebih dahulu.

> [!NOTE]
> Jangan mengedit file indeks ini secara manual. File ini diperbarui secara otomatis oleh `scripts/make_index.py` selama proses kompilasi.

---

## 📚 Sumber Mentah Terkompilasi

| Judul | File Sumber | Tanggal Ditambahkan | Tag |
| :--- | :--- | :--- | :--- |
| [[source-DeepSeek-2025-id]] | `raw/papers/DeepSeek-2025.pdf` | 2026-06-03 | `ingested`, `RL`, `reasoning`, `deepseek`, `grpo` |
| [[source-Krizhevsky-2012-id]] | `raw/papers/Krizhevsky-2012.pdf` | 2026-06-03 | `ingested`, `Krizhevsky-2012`, `cnn`, `relu`, `dropout`, `imagenet` |
| [[source-llm-wiki-id]] | `raw/articles/llm-wiki.md` | 2026-06-03 | `llm-wiki`, `knowledge-base`, `system-design`, `obsidian` |
| [[source-NIPS-2017-attention-is-all-you-need-Paper-id]] | `C:/Users/mifta/Documents/Obsidian Vault/remote-blog/01-TODO/2026/My-Wiki/raw/papers/NIPS-2017-attention-is-all-you-need-Paper.pdf` | 2026-06-03 | `ingested`, `paper`, `transformer`, `attention`, `deep-learning` |
| [[source-Ouyang-2022-id]] | `raw/papers/Ouyang-2022.pdf` | 2026-06-03 | `ingested`, `RLHF`, `alignment`, `instructgpt` |
| [[source-Rombach-2022-id]] | `raw/papers/Rombach-2022.pdf` | 2026-06-03 | `ingested`, `diffusion`, `LDM`, `image-synthesis`, `generative-ai` |
| [[source-2509.20820v1-id]] | `raw/papers/2509.20820v1.pdf` | 2026-06-02 | `in-context-learning`, `prompt-engineering`, `LLM-efficiency`, `knowledge-distillation`, `many-shot-ICL` |
| [[source-the-unreasonable-effectiveness-of-html-id]] | `raw/articles/The Unreasonable Effectiveness Of HTML.md` | 2026-06-02 | `html`, `agent-ui`, `web-design`, `claude-code`, `anthropic` |


## 💡 Konsep Inti per Ranah

### 💻 Rekayasa Perangkat Lunak

#### #agent-ui
- [[agent-html-artifacts-id]] — Paradigma di mana AI coding agent menghasilkan file HTML interaktif dan ber-style penuh alih-alih Markdown biasa untuk meningkatkan dokumentasi dan kolaborasi human-in-the-loop. (🌐 [[agent-html-artifacts]])
- [[html-maximalism-id]] — Filosofi rekayasa yang memprioritaskan HTML asli daripada Markdown untuk hasil kerja AI agent yang kompleks guna memaksimalkan keterbacaan manusia dan interaksi dua arah. (🌐 [[html-maximalism]])

#### #design-pattern
- [[llm-wiki-pattern-id]] — Pola desain sistem di mana agen LLM secara inkremental memelihara wiki berbasis Markdown yang persisten, terstruktur, dan saling tertaut untuk mengompilasi dan menumpuk pengetahuan dari berbagai dokumen sumber. (🌐 [[llm-wiki-pattern]])

#### #html-maximalism
- [[agent-html-artifacts-id]] — Paradigma di mana AI coding agent menghasilkan file HTML interaktif dan ber-style penuh alih-alih Markdown biasa untuk meningkatkan dokumentasi dan kolaborasi human-in-the-loop. (🌐 [[agent-html-artifacts]])
- [[html-maximalism-id]] — Filosofi rekayasa yang memprioritaskan HTML asli daripada Markdown untuk hasil kerja AI agent yang kompleks guna memaksimalkan keterbacaan manusia dan interaksi dua arah. (🌐 [[html-maximalism]])

#### #ingest
- [[agent-html-artifacts-id]] — Paradigma di mana AI coding agent menghasilkan file HTML interaktif dan ber-style penuh alih-alih Markdown biasa untuk meningkatkan dokumentasi dan kolaborasi human-in-the-loop. (🌐 [[agent-html-artifacts]])
- [[html-maximalism-id]] — Filosofi rekayasa yang memprioritaskan HTML asli daripada Markdown untuk hasil kerja AI agent yang kompleks guna memaksimalkan keterbacaan manusia dan interaksi dua arah. (🌐 [[html-maximalism]])

#### #llm-wiki
- [[llm-wiki-pattern-id]] — Pola desain sistem di mana agen LLM secara inkremental memelihara wiki berbasis Markdown yang persisten, terstruktur, dan saling tertaut untuk mengompilasi dan menumpuk pengetahuan dari berbagai dokumen sumber. (🌐 [[llm-wiki-pattern]])

#### #system-design
- [[llm-wiki-pattern-id]] — Pola desain sistem di mana agen LLM secara inkremental memelihara wiki berbasis Markdown yang persisten, terstruktur, dan saling tertaut untuk mengompilasi dan menumpuk pengetahuan dari berbagai dokumen sumber. (🌐 [[llm-wiki-pattern]])

#### #user-interface
- [[agent-html-artifacts-id]] — Paradigma di mana AI coding agent menghasilkan file HTML interaktif dan ber-style penuh alih-alih Markdown biasa untuk meningkatkan dokumentasi dan kolaborasi human-in-the-loop. (🌐 [[agent-html-artifacts]])

#### #web-development
- [[html-maximalism-id]] — Filosofi rekayasa yang memprioritaskan HTML asli daripada Markdown untuk hasil kerja AI agent yang kompleks guna memaksimalkan keterbacaan manusia dan interaksi dua arah. (🌐 [[html-maximalism]])

---
### 🧠 Kecerdasan Buatan

#### #ICL
- [[x-icl-id]] — Kerangka kerja pembelajaran dalam konteks yang melengkapi demonstrasi few-shot atau many-shot dengan penalaran langkah-demi-langkah (rationales), menggunakan sinyal penguatan untuk memilih atau menyempurnakan demonstrasi tersebut. (🌐 [[x-icl]])

#### #LLM
- [[chain-of-thought-prompting-id]] — Teknik pembuatan prompt yang memicu penalaran langkah-demi-langkah dari LLM dengan menyertakan langkah penalaran perantara dalam demonstrasi, yang secara signifikan meningkatkan kinerja pada tugas-tugas kompleks. (🌐 [[chain-of-thought-prompting]])
- [[distilasi-pengetahuan]] — Teknik kompresi model di mana model 'student' yang lebih kecil dilatih untuk meniru perilaku dan distribusi keluaran dari model 'teacher' yang lebih besar dan berkinerja tinggi. (🌐 [[knowledge-distillation]])
- [[many-shot-in-context-learning-id]] — Rezim ICL yang memberikan ratusan atau ribuan contoh demonstrasi ke LLM dengan memanfaatkan context window yang diperluas, menghasilkan kinerja yang unggul dibandingkan few-shot ICL konvensional pada tugas pengenalan pola. (🌐 [[many-shot-in-context-learning]])
- [[pembelajaran-dalam-konteks]] — Paradigma dalam pemrosesan bahasa alami di mana model bahasa besar belajar melakukan tugas melalui contoh demonstrasi masukan-target yang disediakan dalam promptnya, tanpa ada pembaruan parameter. (🌐 [[in-context-learning]])

#### #LLM-efficiency
- [[cheat-sheet-icl-id]] — Metode yang mereduksi demonstrasi Many-Shot ICL menjadi ringkasan tekstual ringkas (cheat sheet) untuk digunakan sebagai konteks saat inferensi, mencapai kinerja sebanding dengan token yang jauh lebih sedikit. (🌐 [[cheat-sheet-icl]])
- [[kompresi-prompt]] — Teknik untuk mengurangi panjang prompt LLM sambil mempertahankan konten informasionalnya, mencakup kompresi demonstrasi dan kompresi masukan RAG. (🌐 [[prompt-compression]])

#### #LLM-evaluation
- [[big-bench-hard-id]] — Kumpulan tugas penalaran menantang yang diturunkan dari BIG-Bench, dikurasi secara khusus agar cukup sulit sehingga memerlukan chain-of-thought prompting untuk meningkatkan kinerja. (🌐 [[big-bench-hard]])

#### #activation-function
- [[relu-nonlinearity-id]] — Fungsi aktivasi non-saturating yang didefinisikan sebagai f(x) = max(0, x) yang mempercepat pelatihan neural network. (🌐 [[relu-nonlinearity]])
- [[softmax-id]] — Fungsi aktivasi yang menormalisasi vektor berisi K bilangan riil menjadi distribusi probabilitas yang terdiri dari K probabilitas. (🌐 [[softmax]])

#### #algorithm
- [[group-relative-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang memperkirakan baseline dari skor rata-rata grup alih-alih mempertahankan jaringan kritikus. (🌐 [[group-relative-policy-optimization]])
- [[proximal-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang menggunakan fungsi objektif terpotong untuk memastikan pembaruan kebijakan yang stabil dan inkremental. (🌐 [[proximal-policy-optimization]])

#### #alignment
- [[pajak-penyelarasan]] — Penurunan performa atau regresi kemampuan pada tolok ukur NLP standar yang terjadi akibat proses penyelarasan model dengan preferensi manusia. (🌐 [[alignment-tax]])
- [[pemodelan-reward]] — Melatih model untuk menghasilkan skor skalar yang mewakili peringkat preferensi manusia untuk pasangan input-output tertentu. (🌐 [[reward-modeling]])
- [[reinforcement-learning-dari-umpan-balik-manusia]] — Paradigma optimasi yang menggunakan peringkat preferensi manusia sebagai sinyal reward untuk menyelaraskan model pembelajaran mesin dengan nilai dan niat manusia. (🌐 [[reinforcement-learning-from-human-feedback]])

#### #alignment-tax
- [[pajak-penyelarasan]] — Penurunan performa atau regresi kemampuan pada tolok ukur NLP standar yang terjadi akibat proses penyelarasan model dengan preferensi manusia. (🌐 [[alignment-tax]])

#### #attention
- [[self-attention-mechanism-id]] — Mekanisme atensi yang menghubungkan posisi-posisi berbeda dari satu sekuens tunggal untuk menghitung representasi dari sekuens tersebut. (🌐 [[self-attention-mechanism]])
- [[transformer-architecture-id]] — Arsitektur model transduksi sekuens yang didasarkan sepenuhnya pada mekanisme self-attention, menghilangkan rekurensi dan konvolusi secara keseluruhan. (🌐 [[transformer-architecture]])

#### #autoencoder
- [[perceptual-image-compression-id]] — Metode autoencoding dua tahap yang memproyeksikan gambar ke dalam ruang dimensi rendah yang setara secara persepsi, menghilangkan detail frekuensi tinggi sambil mempertahankan struktur semantik. (🌐 [[perceptual-image-compression]])

#### #benchmark
- [[big-bench-hard-id]] — Kumpulan tugas penalaran menantang yang diturunkan dari BIG-Bench, dikurasi secara khusus agar cukup sulit sehingga memerlukan chain-of-thought prompting untuk meningkatkan kinerja. (🌐 [[big-bench-hard]])

#### #chain-of-thought
- [[reinforced-icl-id]] — Baseline ICL yang ditingkatkan dengan melengkapi demonstrasi dengan penjelasan penalaran (rationale) model-generated CoT, menyaring penalaran yang benar untuk mendongkrak performa. (🌐 [[reinforced-icl]])

#### #cnn
- [[deep-convolutional-neural-networks-id]] — Kelas neural network mendalam yang umum diterapkan untuk menganalisis citra visual, menggunakan convolutional layers untuk menangkap hierarki spasial. (🌐 [[deep-convolutional-neural-networks]])

#### #compression
- [[kompresi-prompt]] — Teknik untuk mengurangi panjang prompt LLM sambil mempertahankan konten informasionalnya, mencakup kompresi demonstrasi dan kompresi masukan RAG. (🌐 [[prompt-compression]])
- [[perceptual-image-compression-id]] — Metode autoencoding dua tahap yang memproyeksikan gambar ke dalam ruang dimensi rendah yang setara secara persepsi, menghilangkan detail frekuensi tinggi sambil mempertahankan struktur semantik. (🌐 [[perceptual-image-compression]])

#### #computer-vision
- [[deep-convolutional-neural-networks-id]] — Kelas neural network mendalam yang umum diterapkan untuk menganalisis citra visual, menggunakan convolutional layers untuk menangkap hierarki spasial. (🌐 [[deep-convolutional-neural-networks]])
- [[perceptual-image-compression-id]] — Metode autoencoding dua tahap yang memproyeksikan gambar ke dalam ruang dimensi rendah yang setara secara persepsi, menghilangkan detail frekuensi tinggi sambil mempertahankan struktur semantik. (🌐 [[perceptual-image-compression]])

#### #deep-learning
- [[deep-convolutional-neural-networks-id]] — Kelas neural network mendalam yang umum diterapkan untuk menganalisis citra visual, menggunakan convolutional layers untuk menangkap hierarki spasial. (🌐 [[deep-convolutional-neural-networks]])
- [[dropout-regularization-id]] — Teknik regularisasi di mana neuron tersembunyi secara acak disetel ke nol selama pelatihan dengan probabilitas tertentu untuk mencegah co-adaptation. (🌐 [[dropout-regularization]])
- [[relu-nonlinearity-id]] — Fungsi aktivasi non-saturating yang didefinisikan sebagai f(x) = max(0, x) yang mempercepat pelatihan neural network. (🌐 [[relu-nonlinearity]])
- [[self-attention-mechanism-id]] — Mekanisme atensi yang menghubungkan posisi-posisi berbeda dari satu sekuens tunggal untuk menghitung representasi dari sekuens tersebut. (🌐 [[self-attention-mechanism]])
- [[softmax-id]] — Fungsi aktivasi yang menormalisasi vektor berisi K bilangan riil menjadi distribusi probabilitas yang terdiri dari K probabilitas. (🌐 [[softmax]])
- [[supervised-fine-tuning-id]] — Proses melakukan fine-tuning pada model bahasa yang telah dilatih sebelumnya menggunakan kumpulan data prompt-demonstrasi berkualitas tinggi lewat pembelajaran terawasi. (🌐 [[supervised-fine-tuning]])
- [[transformer-architecture-id]] — Arsitektur model transduksi sekuens yang didasarkan sepenuhnya pada mekanisme self-attention, menghilangkan rekurensi dan konvolusi secara keseluruhan. (🌐 [[transformer-architecture]])

#### #demonstration-selection
- [[demonstration-retrieval-for-icl-id]] — Strategi untuk ICL yang mengambil contoh demonstrasi tugas serupa dengan setiap masukan uji dari kumpulan data yang lebih besar, meningkatkan kinerja sekaligus menjaga konteks tetap singkat. (🌐 [[demonstration-retrieval-for-icl]])

#### #diffusion
- [[model-difusi-laten]] — Kelas model difusi probabilistik yang beroperasi di dalam ruang laten berdimensi lebih rendah dari autoencoder yang telah dilatih sebelumnya untuk menghasilkan data resolusi tinggi secara efisien. (🌐 [[latent-diffusion-models]])

#### #efficiency
- [[distilasi-pengetahuan]] — Teknik kompresi model di mana model 'student' yang lebih kecil dilatih untuk meniru perilaku dan distribusi keluaran dari model 'teacher' yang lebih besar dan berkinerja tinggi. (🌐 [[knowledge-distillation]])

#### #evaluation
- [[pajak-penyelarasan]] — Penurunan performa atau regresi kemampuan pada tolok ukur NLP standar yang terjadi akibat proses penyelarasan model dengan preferensi manusia. (🌐 [[alignment-tax]])

#### #few-shot-learning
- [[many-shot-in-context-learning-id]] — Rezim ICL yang memberikan ratusan atau ribuan contoh demonstrasi ke LLM dengan memanfaatkan context window yang diperluas, menghasilkan kinerja yang unggul dibandingkan few-shot ICL konvensional pada tugas pengenalan pola. (🌐 [[many-shot-in-context-learning]])
- [[pembelajaran-dalam-konteks]] — Paradigma dalam pemrosesan bahasa alami di mana model bahasa besar belajar melakukan tugas melalui contoh demonstrasi masukan-target yang disediakan dalam promptnya, tanpa ada pembaruan parameter. (🌐 [[in-context-learning]])
- [[x-icl-id]] — Kerangka kerja pembelajaran dalam konteks yang melengkapi demonstrasi few-shot atau many-shot dengan penalaran langkah-demi-langkah (rationales), menggunakan sinyal penguatan untuk memilih atau menyempurnakan demonstrasi tersebut. (🌐 [[x-icl]])

#### #fine-tuning
- [[supervised-fine-tuning-id]] — Proses melakukan fine-tuning pada model bahasa yang telah dilatih sebelumnya menggunakan kumpulan data prompt-demonstrasi berkualitas tinggi lewat pembelajaran terawasi. (🌐 [[supervised-fine-tuning]])

#### #generative-model
- [[model-difusi-laten]] — Kelas model difusi probabilistik yang beroperasi di dalam ruang laten berdimensi lebih rendah dari autoencoder yang telah dilatih sebelumnya untuk menghasilkan data resolusi tinggi secara efisien. (🌐 [[latent-diffusion-models]])

#### #grpo
- [[group-relative-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang memperkirakan baseline dari skor rata-rata grup alih-alih mempertahankan jaringan kritikus. (🌐 [[group-relative-policy-optimization]])

#### #image-synthesis
- [[model-difusi-laten]] — Kelas model difusi probabilistik yang beroperasi di dalam ruang laten berdimensi lebih rendah dari autoencoder yang telah dilatih sebelumnya untuk menghasilkan data resolusi tinggi secara efisien. (🌐 [[latent-diffusion-models]])

#### #in-context-learning
- [[cheat-sheet-icl-id]] — Metode yang mereduksi demonstrasi Many-Shot ICL menjadi ringkasan tekstual ringkas (cheat sheet) untuk digunakan sebagai konteks saat inferensi, mencapai kinerja sebanding dengan token yang jauh lebih sedikit. (🌐 [[cheat-sheet-icl]])
- [[demonstration-retrieval-for-icl-id]] — Strategi untuk ICL yang mengambil contoh demonstrasi tugas serupa dengan setiap masukan uji dari kumpulan data yang lebih besar, meningkatkan kinerja sekaligus menjaga konteks tetap singkat. (🌐 [[demonstration-retrieval-for-icl]])
- [[many-shot-in-context-learning-id]] — Rezim ICL yang memberikan ratusan atau ribuan contoh demonstrasi ke LLM dengan memanfaatkan context window yang diperluas, menghasilkan kinerja yang unggul dibandingkan few-shot ICL konvensional pada tugas pengenalan pola. (🌐 [[many-shot-in-context-learning]])
- [[pembelajaran-dalam-konteks]] — Paradigma dalam pemrosesan bahasa alami di mana model bahasa besar belajar melakukan tugas melalui contoh demonstrasi masukan-target yang disediakan dalam promptnya, tanpa ada pembaruan parameter. (🌐 [[in-context-learning]])
- [[reinforced-icl-id]] — Baseline ICL yang ditingkatkan dengan melengkapi demonstrasi dengan penjelasan penalaran (rationale) model-generated CoT, menyaring penalaran yang benar untuk mendongkrak performa. (🌐 [[reinforced-icl]])

#### #ingest
- [[deep-convolutional-neural-networks-id]] — Kelas neural network mendalam yang umum diterapkan untuk menganalisis citra visual, menggunakan convolutional layers untuk menangkap hierarki spasial. (🌐 [[deep-convolutional-neural-networks]])
- [[dropout-regularization-id]] — Teknik regularisasi di mana neuron tersembunyi secara acak disetel ke nol selama pelatihan dengan probabilitas tertentu untuk mencegah co-adaptation. (🌐 [[dropout-regularization]])
- [[relu-nonlinearity-id]] — Fungsi aktivasi non-saturating yang didefinisikan sebagai f(x) = max(0, x) yang mempercepat pelatihan neural network. (🌐 [[relu-nonlinearity]])
- [[self-attention-mechanism-id]] — Mekanisme atensi yang menghubungkan posisi-posisi berbeda dari satu sekuens tunggal untuk menghitung representasi dari sekuens tersebut. (🌐 [[self-attention-mechanism]])
- [[transformer-architecture-id]] — Arsitektur model transduksi sekuens yang didasarkan sepenuhnya pada mekanisme self-attention, menghilangkan rekurensi dan konvolusi secara keseluruhan. (🌐 [[transformer-architecture]])

#### #knowledge-distillation
- [[cheat-sheet-icl-id]] — Metode yang mereduksi demonstrasi Many-Shot ICL menjadi ringkasan tekstual ringkas (cheat sheet) untuk digunakan sebagai konteks saat inferensi, mencapai kinerja sebanding dengan token yang jauh lebih sedikit. (🌐 [[cheat-sheet-icl]])
- [[distilasi-pengetahuan]] — Teknik kompresi model di mana model 'student' yang lebih kecil dilatih untuk meniru perilaku dan distribusi keluaran dari model 'teacher' yang lebih besar dan berkinerja tinggi. (🌐 [[knowledge-distillation]])

#### #latent-diffusion
- [[model-difusi-laten]] — Kelas model difusi probabilistik yang beroperasi di dalam ruang laten berdimensi lebih rendah dari autoencoder yang telah dilatih sebelumnya untuk menghasilkan data resolusi tinggi secara efisien. (🌐 [[latent-diffusion-models]])

#### #latent-space
- [[perceptual-image-compression-id]] — Metode autoencoding dua tahap yang memproyeksikan gambar ke dalam ruang dimensi rendah yang setara secara persepsi, menghilangkan detail frekuensi tinggi sambil mempertahankan struktur semantik. (🌐 [[perceptual-image-compression]])

#### #long-context
- [[many-shot-in-context-learning-id]] — Rezim ICL yang memberikan ratusan atau ribuan contoh demonstrasi ke LLM dengan memanfaatkan context window yang diperluas, menghasilkan kinerja yang unggul dibandingkan few-shot ICL konvensional pada tugas pengenalan pola. (🌐 [[many-shot-in-context-learning]])

#### #machine-learning
- [[reinforcement-learning-dari-umpan-balik-manusia]] — Paradigma optimasi yang menggunakan peringkat preferensi manusia sebagai sinyal reward untuk menyelaraskan model pembelajaran mesin dengan nilai dan niat manusia. (🌐 [[reinforcement-learning-from-human-feedback]])

#### #model-compression
- [[distilasi-pengetahuan]] — Teknik kompresi model di mana model 'student' yang lebih kecil dilatih untuk meniru perilaku dan distribusi keluaran dari model 'teacher' yang lebih besar dan berkinerja tinggi. (🌐 [[knowledge-distillation]])

#### #neural-network
- [[deep-convolutional-neural-networks-id]] — Kelas neural network mendalam yang umum diterapkan untuk menganalisis citra visual, menggunakan convolutional layers untuk menangkap hierarki spasial. (🌐 [[deep-convolutional-neural-networks]])
- [[dropout-regularization-id]] — Teknik regularisasi di mana neuron tersembunyi secara acak disetel ke nol selama pelatihan dengan probabilitas tertentu untuk mencegah co-adaptation. (🌐 [[dropout-regularization]])
- [[relu-nonlinearity-id]] — Fungsi aktivasi non-saturating yang didefinisikan sebagai f(x) = max(0, x) yang mempercepat pelatihan neural network. (🌐 [[relu-nonlinearity]])
- [[softmax-id]] — Fungsi aktivasi yang menormalisasi vektor berisi K bilangan riil menjadi distribusi probabilitas yang terdiri dari K probabilitas. (🌐 [[softmax]])

#### #neural-networks
- [[self-attention-mechanism-id]] — Mekanisme atensi yang menghubungkan posisi-posisi berbeda dari satu sekuens tunggal untuk menghitung representasi dari sekuens tersebut. (🌐 [[self-attention-mechanism]])
- [[transformer-architecture-id]] — Arsitektur model transduksi sekuens yang didasarkan sepenuhnya pada mekanisme self-attention, menghilangkan rekurensi dan konvolusi secara keseluruhan. (🌐 [[transformer-architecture]])

#### #optimization
- [[group-relative-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang memperkirakan baseline dari skor rata-rata grup alih-alih mempertahankan jaringan kritikus. (🌐 [[group-relative-policy-optimization]])
- [[proximal-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang menggunakan fungsi objektif terpotong untuk memastikan pembaruan kebijakan yang stabil dan inkremental. (🌐 [[proximal-policy-optimization]])
- [[reinforcement-learning-dari-umpan-balik-manusia]] — Paradigma optimasi yang menggunakan peringkat preferensi manusia sebagai sinyal reward untuk menyelaraskan model pembelajaran mesin dengan nilai dan niat manusia. (🌐 [[reinforcement-learning-from-human-feedback]])

#### #overfitting
- [[dropout-regularization-id]] — Teknik regularisasi di mana neuron tersembunyi secara acak disetel ke nol selama pelatihan dengan probabilitas tertentu untuk mencegah co-adaptation. (🌐 [[dropout-regularization]])

#### #ppo
- [[proximal-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang menggunakan fungsi objektif terpotong untuk memastikan pembaruan kebijakan yang stabil dan inkremental. (🌐 [[proximal-policy-optimization]])

#### #preference-learning
- [[pemodelan-reward]] — Melatih model untuk menghasilkan skor skalar yang mewakili peringkat preferensi manusia untuk pasangan input-output tertentu. (🌐 [[reward-modeling]])

#### #prompt-engineering
- [[cheat-sheet-icl-id]] — Metode yang mereduksi demonstrasi Many-Shot ICL menjadi ringkasan tekstual ringkas (cheat sheet) untuk digunakan sebagai konteks saat inferensi, mencapai kinerja sebanding dengan token yang jauh lebih sedikit. (🌐 [[cheat-sheet-icl]])
- [[kompresi-prompt]] — Teknik untuk mengurangi panjang prompt LLM sambil mempertahankan konten informasionalnya, mencakup kompresi demonstrasi dan kompresi masukan RAG. (🌐 [[prompt-compression]])
- [[pembelajaran-dalam-konteks]] — Paradigma dalam pemrosesan bahasa alami di mana model bahasa besar belajar melakukan tugas melalui contoh demonstrasi masukan-target yang disediakan dalam promptnya, tanpa ada pembaruan parameter. (🌐 [[in-context-learning]])

#### #prompting
- [[chain-of-thought-prompting-id]] — Teknik pembuatan prompt yang memicu penalaran langkah-demi-langkah dari LLM dengan menyertakan langkah penalaran perantara dalam demonstrasi, yang secara signifikan meningkatkan kinerja pada tugas-tugas kompleks. (🌐 [[chain-of-thought-prompting]])

#### #rationale-augmentation
- [[reinforced-icl-id]] — Baseline ICL yang ditingkatkan dengan melengkapi demonstrasi dengan penjelasan penalaran (rationale) model-generated CoT, menyaring penalaran yang benar untuk mendongkrak performa. (🌐 [[reinforced-icl]])

#### #rationales
- [[x-icl-id]] — Kerangka kerja pembelajaran dalam konteks yang melengkapi demonstrasi few-shot atau many-shot dengan penalaran langkah-demi-langkah (rationales), menggunakan sinyal penguatan untuk memilih atau menyempurnakan demonstrasi tersebut. (🌐 [[x-icl]])

#### #reasoning
- [[big-bench-hard-id]] — Kumpulan tugas penalaran menantang yang diturunkan dari BIG-Bench, dikurasi secara khusus agar cukup sulit sehingga memerlukan chain-of-thought prompting untuk meningkatkan kinerja. (🌐 [[big-bench-hard]])
- [[chain-of-thought-prompting-id]] — Teknik pembuatan prompt yang memicu penalaran langkah-demi-langkah dari LLM dengan menyertakan langkah penalaran perantara dalam demonstrasi, yang secara signifikan meningkatkan kinerja pada tugas-tugas kompleks. (🌐 [[chain-of-thought-prompting]])

#### #regularization
- [[dropout-regularization-id]] — Teknik regularisasi di mana neuron tersembunyi secara acak disetel ke nol selama pelatihan dengan probabilitas tertentu untuk mencegah co-adaptation. (🌐 [[dropout-regularization]])

#### #reinforced-icl
- [[x-icl-id]] — Kerangka kerja pembelajaran dalam konteks yang melengkapi demonstrasi few-shot atau many-shot dengan penalaran langkah-demi-langkah (rationales), menggunakan sinyal penguatan untuk memilih atau menyempurnakan demonstrasi tersebut. (🌐 [[x-icl]])

#### #reinforcement-learning
- [[group-relative-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang memperkirakan baseline dari skor rata-rata grup alih-alih mempertahankan jaringan kritikus. (🌐 [[group-relative-policy-optimization]])
- [[proximal-policy-optimization-id]] — Algoritme reinforcement learning gradien kebijakan yang menggunakan fungsi objektif terpotong untuk memastikan pembaruan kebijakan yang stabil dan inkremental. (🌐 [[proximal-policy-optimization]])

#### #retrieval
- [[demonstration-retrieval-for-icl-id]] — Strategi untuk ICL yang mengambil contoh demonstrasi tugas serupa dengan setiap masukan uji dari kumpulan data yang lebih besar, meningkatkan kinerja sekaligus menjaga konteks tetap singkat. (🌐 [[demonstration-retrieval-for-icl]])

#### #reward-model
- [[pemodelan-reward]] — Melatih model untuk menghasilkan skor skalar yang mewakili peringkat preferensi manusia untuk pasangan input-output tertentu. (🌐 [[reward-modeling]])

#### #rlhf
- [[reinforcement-learning-dari-umpan-balik-manusia]] — Paradigma optimasi yang menggunakan peringkat preferensi manusia sebagai sinyal reward untuk menyelaraskan model pembelajaran mesin dengan nilai dan niat manusia. (🌐 [[reinforcement-learning-from-human-feedback]])

#### #rm
- [[pemodelan-reward]] — Melatih model untuk menghasilkan skor skalar yang mewakili peringkat preferensi manusia untuk pasangan input-output tertentu. (🌐 [[reward-modeling]])

#### #safety
- [[pajak-penyelarasan]] — Penurunan performa atau regresi kemampuan pada tolok ukur NLP standar yang terjadi akibat proses penyelarasan model dengan preferensi manusia. (🌐 [[alignment-tax]])

#### #self-attention
- [[self-attention-mechanism-id]] — Mekanisme atensi yang menghubungkan posisi-posisi berbeda dari satu sekuens tunggal untuk menghitung representasi dari sekuens tersebut. (🌐 [[self-attention-mechanism]])

#### #sft
- [[supervised-fine-tuning-id]] — Proses melakukan fine-tuning pada model bahasa yang telah dilatih sebelumnya menggunakan kumpulan data prompt-demonstrasi berkualitas tinggi lewat pembelajaran terawasi. (🌐 [[supervised-fine-tuning]])

#### #training
- [[supervised-fine-tuning-id]] — Proses melakukan fine-tuning pada model bahasa yang telah dilatih sebelumnya menggunakan kumpulan data prompt-demonstrasi berkualitas tinggi lewat pembelajaran terawasi. (🌐 [[supervised-fine-tuning]])

#### #transformer
- [[transformer-architecture-id]] — Arsitektur model transduksi sekuens yang didasarkan sepenuhnya pada mekanisme self-attention, menghilangkan rekurensi dan konvolusi secara keseluruhan. (🌐 [[transformer-architecture]])

#### #x-icl
- [[x-icl-id]] — Kerangka kerja pembelajaran dalam konteks yang melengkapi demonstrasi few-shot atau many-shot dengan penalaran langkah-demi-langkah (rationales), menggunakan sinyal penguatan untuk memilih atau menyempurnakan demonstrasi tersebut. (🌐 [[x-icl]])

---

## 👥 Entitas Terkait per Ranah

### Entitas 💻 Rekayasa Perangkat Lunak

#### Tokoh / Individu
- [[thariq-shihipar-id]] #anthropic #claude-code #developer #engineer (🌐 [[thariq-shihipar]])
- [[vannevar-bush-id]] #history #pioneer (🌐 [[vannevar-bush]])

#### Alat & Perangkat Lunak
- [[claude-code-id]] #cli #agent #ai-coding-assistant #anthropic (🌐 [[claude-code]])
- [[memex-id]] #history #hypertext (🌐 [[memex]])

#### Entitas Lainnya
- [[obsidian-id]] #knowledge-base #markdown #obsidian (🌐 [[obsidian]])

---
### Entitas 🧠 Kecerdasan Buatan

#### Tokoh / Individu
- [[alex-krizhevsky-id]] #researcher #deep-learning #computer-vision (🌐 [[alex-krizhevsky]])
- [[geoffrey-hinton-id]] #researcher #deep-learning #godfather-of-ai (🌐 [[geoffrey-hinton]])
- [[ilya-sutskever-id]] #researcher #deep-learning #openai (🌐 [[ilya-sutskever]])

#### Organisasi / Perusahaan
- [[anthropic-id]] #ai-research #organization #LLM #claude (🌐 [[anthropic]])
- [[compvis-id]] #compvis #research #lmu #germany #computer-vision (🌐 [[compvis]])
- [[cyberagent-id]] #AI-research #Japan #tech-company (🌐 [[cyberagent]])
- [[imagenet-dataset-id]] #dataset #computer-vision #benchmark (🌐 [[imagenet-dataset]])
- [[openai-id]] #openai #research #organization #artificial-intelligence (🌐 [[openai]])

#### Model & Sistem AI
- [[deepseek-r1-id]] #deepseek #deepseek-r1 #llm #reasoning #RL (🌐 [[deepseek-r1]])
- [[deepseek-r1-zero-id]] #deepseek #deepseek-r1-zero #llm #reasoning #RL (🌐 [[deepseek-r1-zero]])
- [[gemini-2.0-flash-id]] #LLM #Google #proprietary-model (🌐 [[gemini-2.0-flash]])
- [[gpt-4.1-id]] #LLM #OpenAI #proprietary-model (🌐 [[gpt-4.1]])
- [[instructgpt-id]] #instructgpt #gpt-3 #openai #llm (🌐 [[instructgpt]])
- [[stable-diffusion-id]] #stable-diffusion #compvis #generative-ai #text-to-image (🌐 [[stable-diffusion]])

#### Entitas Lainnya
- [[cuda-convnet-id]] #software #tool #gpu #convolution #cuda (🌐 [[cuda-convnet]])

---