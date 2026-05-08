# NutriTrack AI 🥗🤖 

NutriTrack AI, Google Gemini ve Groq (Llama 3.3) yapay zeka modelleriyle güçlendirilmiş, yeni nesil bir **Kişisel Sağlık ve Performans Asistanıdır.** Sadece yediklerinizi takip etmekle kalmaz, aynı zamanda bir spor koçu, mutfak şefi ve veri analisti gibi sizi hedeflerinize ulaştırır.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-emerald.svg)
![Flask](https://img.shields.io/badge/flask-3.0-blue.svg)
![AI](https://img.shields.io/badge/AI-Groq--Llama3.3-orange.svg)

---

## ✨ Öne Çıkan Özellikler

### 🧠 Akıllı Besin Analizi (Natural Language Processing)
"2 yumurta, 1 domates ve 10 zeytin yedim" gibi serbest metinleri saniyeler içinde analiz eder. 
- **Hatasız Hesaplama:** Birim değerleri ve toplam porsiyonları yapay zeka ile çapraz kontrol eder.
- **Dinamik Makro Takibi:** Kalori, protein, karbonhidrat ve yağ dengenizi anlık grafiklerle izleyin.

### 🏋️‍♂️ AI Personal Trainer (PT)
Antrenmanlarınızı detaylıca analiz eden ve teknik geri bildirim veren dijital antrenörünüz.
- **Performans Takibi:** Kaldırdığınız ağırlıkları (kg/set/tekrar) otomatik ayıklar ve kaydeder.
- **Progressive Overload Analizi:** Geçen haftaya göre ne kadar güçlendiğinizi tespit eder ve profesyonel yorum yapar.

### 👨‍🍳 AI Mutfak Şefi & Buzdolabı Asistanı
"Evde ne pişirsem?" derdine son!
- Elinizdeki malzemeleri yazın, AI sizin güncel diyet hedefinize (Kilo verme, Kas kazanımı vb.) en uygun sağlıklı tarifi hazırlasın.

### 📉 Gelişim ve Kilo Takibi
- Kilonuzu düzenli kaydedin ve değişim grafiğini izleyin.
- **Akıllı Hedefleme:** Kilonuz değiştikçe günlük kalori ve makro ihtiyaçlarınız (Mifflin-St Jeor) otomatik olarak güncellenir.

### 💧 Akıllı Hidrasyon Paneli
- Günlük su tüketiminizi interaktif ve görselleştirilmiş bir bar üzerinden takip edin.

---

## 🛠️ Teknik Altyapı

- **Backend:** Python / Flask
- **Database:** SQLAlchemy ORM (SQL Server / SQLite uyumlu)
- **AI Engine:** Groq API (Llama 3.3 70B Versatile)
- **Frontend:** HTML5, CSS3, Tailwind CSS (Glassmorphism UI)
- **Visuals:** Chart.js, FontAwesome 6

---

## 🚀 Kurulum ve Çalıştırma

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/kullanici_adiniz/NutriTrack-AI.git
   cd NutriTrack-AI
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **API Anahtarınızı Ayarlayın:**
   `.env` dosyasını oluşturun veya `.env.example` üzerinden kopyalayın:
   ```env
   SECRET_KEY=gizli_anahtariniz
   DATABASE_URL=mssql+pyodbc://... (veya sqlite:///app.db)
   GROQ_API_KEY=gsk_sizin_groq_anahtariniz
   ```

4. **Veritabanını Hazırlayın:**
   ```bash
   flask db upgrade
   ```

5. **Uygulamayı Başlatın:**
   ```bash
   python run.py
   ```

---

## 🗺️ Yakında Gelecek Özellikler (Roadmap)

- [ ] **AI Sabah Brifingi:** Her sabah verilerinizi analiz eden kişiye özel günlük strateji mesajı.
- [ ] **NutriScore & Streak:** Hedeflere uyum sağladıkça artan skor ve yanmaya başlayan "Ateş" ikonu.
- [ ] **Akıllı Alışveriş Listesi:** Haftalık performansa göre market ihtiyaç listesi.

---

## 📄 Lisans
Bu proje MIT Lisansı ile korunmaktadır.

---
*NutriTrack AI - Sağlıklı yaşamın en akıllı yolu.* 🚀
