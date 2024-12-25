# Gemini AI Sohbet Arayüzü

Bu proje, Google'ın Gemini AI modelini kullanan, Python ve Tkinter ile geliştirilmiş basit bir sohbet uygulamasıdır. Kullanıcıların Gemini AI ile etkileşime girmesini sağlayan kullanıcı dostu bir arayüz sunar.

## Özellikler

- 🤖 Gemini AI ile gerçek zamanlı sohbet
- 💬 Kelime kelime metin akışı
- ⚡ Yanıt oluşturmayı iptal edebilme
- 📱 Yeniden boyutlandırılabilir arayüz
- 🌐 Çoklu model desteği (.env üzerinden yapılandırılabilir)

## Gereksinimler

- Python 3.x
- google-generativeai
- python-dotenv
- tkinter (Python ile birlikte gelir)

## Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/gemini-chat-gui.git
   cd gemini-chat-gui
   ```

2. Sanal ortam oluşturun ve etkinleştirin:
   ```bash
   python -m venv venv
   # Windows için:
   venv\Scripts\activate
   # Linux/Mac için:
   source venv/bin/activate
   ```

3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. `.env` dosyası oluşturun:
   ```plaintext
   GEMINI_API_KEY="your-api-key-here"
   GEMINI_MODEL="gemini-pro"
   ```

## Kullanım

1. Uygulamayı başlatın:
   ```bash
   python gui.py
   ```