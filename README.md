# GNN Image Resize

**GNN Image Resize** is an open-source, user-friendly image resizing tool with multi-format support and batch processing capability.

With its intuitive interface and flexible settings, it’s suitable for both basic and advanced resizing needs.

---
[https://i.imgur.com/K7CHFBf.png](https://i.imgur.com/K7CHFBf.png)
---

## ✨ Features

- **Multi-format support:** JPEG, PNG, BMP, GIF, and more.
- **Batch processing:** Resize multiple images at once.
- **Scaling options:** By percentage or exact pixel dimensions.
- **DPI adjustment:** Set DPI (72–300).
- **EXIF preservation:** Keep image metadata if possible.
- **Quality control:** Adjustable output quality (1–100).
- **Filtering options:** LANCZOS, BICUBIC, BILINEAR, NEAREST, BOX, HAMMING.
- **Output format selection:** Keep original or convert to another format.
- **Offline:** Works fully offline, no data leaves your device.

---

## 📥 Installation & Usage

### 1) Download the Executable
Get the `.exe` from the [Releases](../../releases) page and run it.

### 2) Run from Source
```bash
git clone https://github.com/BigDesigner/GNN-Image-Resize.git
cd GNN-Image-Resize
pip install -r requirements.txt
python gnn_image_resize.py
```

### 3) Build your own .exe (PyInstaller)
```bash
pyinstaller --onefile --noconsole --name "GNNImageResize" --icon "icon.ico" --hidden-import PIL._tkinter_finder gnn_image_resize.py
```
💡 Tip: Add `--version-file version_info.txt` if you want to include a version resource.

---

## 🤝 Contributing

This project grows with community support:

1. **Open an Issue:** [Create a new issue](../../issues)
2. **Submit a Pull Request:** Add features or fixes
3. **Join Discussions:** Share ideas in [Discussions](../../discussions)

---

## 📄 License

Licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

> **Note:** The tool works completely offline. No image data leaves your computer.

---

## 🇹🇷 Türkçe Açıklama

**GNN Image Resize**, çoklu format desteği ve toplu işlem özelliği sunan, kullanıcı dostu açık kaynaklı bir görsel boyutlandırma aracıdır.

Sezgisel arayüzü ve esnek ayarları sayesinde hem temel hem de ileri seviye ihtiyaçlar için uygundur.

---
[https://i.imgur.com/K7CHFBf.png](https://i.imgur.com/K7CHFBf.png)
---

### ✨ Özellikler

- **Çoklu format desteği:** JPEG, PNG, BMP, GIF ve daha fazlası.
- **Toplu işlem:** Birden fazla görseli aynı anda boyutlandırma.
- **Ölçekleme seçenekleri:** Yüzde veya piksel cinsinden.
- **DPI ayarı:** DPI değerini belirleyin (72–300).
- **EXIF koruma:** Mümkünse görsel meta verilerini korur.
- **Kalite kontrolü:** Çıktı kalitesini ayarlayın (1–100).
- **Filtre seçenekleri:** LANCZOS, BICUBIC, BILINEAR, NEAREST, BOX, HAMMING.
- **Çıktı formatı seçimi:** Orijinal formatı koruyabilir veya dönüştürebilir.
- **Çevrimdışı çalışma:** Tamamen çevrimdışı çalışır, verileriniz cihazınızdan çıkmaz.

---

### 📥 Kurulum & Kullanım

#### 1) Çalıştırılabilir Dosyayı İndirin
`.exe` dosyasını [Releases](../../releases) sayfasından indirip çalıştırın.

#### 2) Kaynaktan Çalıştırma
```bash
git clone https://github.com/BigDesigner/GNN-Image-Resize.git
cd GNN-Image-Resize
pip install -r requirements.txt
python gnn_image_resize.py
```

#### 3) Kendi .exe Dosyanızı Oluşturun (PyInstaller)
```bash
pyinstaller --onefile --noconsole --name "GNNImageResize" --icon "icon.ico" --hidden-import PIL._tkinter_finder gnn_image_resize.py
```
💡 İpucu: Bir sürüm bilgisi eklemek için `--version-file version_info.txt` parametresini ekleyebilirsiniz.

---

## 🤝 Katkıda Bulunma

Bu proje topluluk desteğiyle gelişmektedir:

1. **Issue Açın:** [Yeni bir issue oluşturun](../../issues)
2. **Pull Request Gönderin:** Özellik ekleyin veya hataları düzeltin
3. **Tartışmalara Katılın:** Fikirlerinizi [Discussions](../../discussions) bölümünde paylaşın

---

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

> **Not:** Araç tamamen çevrimdışı çalışır. Görsel verileriniz cihazınızdan çıkmaz.
