from groq import Groq
import os
import json
from flask import current_app

class AIService:
    def __init__(self):
        try:
            api_key = current_app.config.get('GROQ_API_KEY')
            if not api_key:
                print("DEBUG: [AIService] GROQ_API_KEY is None! Check your .env file.")
            
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile" 
        except Exception as e:
            print(f"DEBUG: [AIService] Failed to initialize Groq: {str(e)}")

    def generate_response(self, user_profile, daily_status, user_query):
        """
        Generates a response from Groq using user context and current macro status.
        """
        try:
            system_prompt = f"""
            Sen bir profesyonel beslenme ve spor koçusun. Kullanıcının adı: {user_profile['username']}.
            
            Kullanıcı Bilgileri:
            - Yaş: {user_profile['age']}, Cinsiyet: {user_profile['gender']}
            - Boy: {user_profile['height']} cm, Kilo: {user_profile['weight']} kg
            - Hedef: {user_profile['goal']}
            
            Bugünkü Beslenme Durumu:
            - Alınan Kalori: {daily_status['calories']} / Hedef: {user_profile['target_calories']}
            - Protein: {daily_status['protein']}g / Hedef: {user_profile['target_protein']}g
            - Karbonhidrat: {daily_status['carbs']}g / Hedef: {user_profile['target_carbs']}g
            - Yağ: {daily_status['fats']}g / Hedef: {user_profile['target_fats']}g
            
            Lütfen kullanıcının hedeflerine uygun, bilimsel temelli ve motive edici bir cevap ver.
            Cevapların kısa, öz ve samimi olsun.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"AI servisi (Groq) şu an yanıt veremiyor: {str(e)}"

    def parse_food_input(self, text):
        """
        Parses free text food input into a structured JSON list of food items.
        """
        try:
            # New strict prompt provided by user
            system_prompt = """
            Sen NutriTrack uygulamasının profesyonel besin analiz motorusun. Görevin kullanıcı girdilerini bilimsel verilere dayalı kalori ve makro değerlerine dönüştürmektir. Şu kurallara SIKI SIKIYA uymalısın:

            BİRİM AYRIMI: Kullanıcı "adet", "tane" veya "dilim" dediğinde bunu asla 100 gramlık porsiyonlarla karıştırma. Eğer kullanıcı gıda miktarını 'adet' veya 'tane' olarak belirtmişse, toplam kaloriyi (adet sayısı * birim kalori) formülüyle hesapla. Örneğin: 1 adet zeytin asla 59 kcal olamaz, 5-6 kcal olmalıdır. 10 adet zeytin için 590 kcal döndürmek yerine 60 kcal döndür.
            Örnek: 1 adet zeytin ~6 kcal'dir (590 değil!).
            Örnek: 1/4 somun ekmek ~160 kcal'dir.
            Örnek: 1 adet yumurta ~78 kcal ve 6g proteindir.

            GENEL BESİN MANTIĞI (Et, Sebze, Meyve):
            * Kullanıcı miktar belirtmezse (örn: "et yedim"), bunu standart 1 porsiyon (pişmiş ~100-120g) olarak kabul et ve yaklaşık 200-250 kcal / 25-30g protein bandında hesapla.
            * "1 avuç", "1 tabak" gibi ifadeleri standart ev ölçülerine göre normalize et.

            MANTIKSAL KONTROL: Hesapladığın toplam kalori miktarı, biyolojik gerçekliğe uygun olmalı. 10 adet zeytin veya 4 yumurta gibi tekil malzemelerin 500 kcal'yi aşması durumunda işlemi durdur ve birim değerlerini tekrar kontrol et.

            HATA ENGELLEME: Sayısal verilerde asla uydurma yapma. Emin olmadığın besinlerde en güvenilir ortalama değerleri kullan.

            ÇIKTI FORMATI:
            Analiz sonuçlarını mutlaka şu JSON formatında bir liste olarak döndür. Başka hiçbir açıklama ekleme.
            [
                {
                    "name": "besin adı",
                    "quantity": 4, 
                    "unit_type": "adet", 
                    "unit_calories": 78,
                    "unit_protein": 6,
                    "total_calories": 312,
                    "total_protein": 24,
                    "total_carbs": 2,
                    "total_fats": 20
                }
            ]
            'unit_calories' 1 adet/100g değeridir. 'total_calories' ise toplam porsiyon değeridir.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Metin: {text}. Sadece JSON döndür."}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            raw_text = completion.choices[0].message.content.strip()
            data = json.loads(raw_text)
            
            # Extract list if wrapped in a key
            if isinstance(data, dict):
                for key in data:
                    if isinstance(data[key], list):
                        return data[key]
                if "name" in data:
                    return [data]
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error parsing food input: {str(e)}")
            return []

    def get_food_recommendations(self, user_profile, daily_status):
        """
        Food recommendation based on remaining macros.
        """
        try:
            remaining_cal = user_profile['target_calories'] - daily_status['calories']
            remaining_pro = user_profile['target_protein'] - daily_status['protein']
            
            prompt = f"""
            Kullanıcının bugün {remaining_cal} kcal ve {remaining_pro}g protein açığı var.
            Hedefi: {user_profile['goal']}.
            Bu açığı kapatmak için 3 farklı öğün/atıştırmalık önerisi yap. 
            Önerilerin makro değerlerini de belirt. Kısa ve öz ol.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Öneri oluşturulamadı: {str(e)}"

    def analyze_workout(self, user_profile, workout_text, workout_history=None):
        """
        Analyzes workout for performance tracking and coaching feedback.
        """
        try:
            history_context = ""
            if workout_history:
                history_context = "Son antrenmanların:\n" + "\n".join([f"- {h['date']}: {h['description']}" for h in workout_history])

            system_prompt = f"""
            Sen NutriTrack uygulamasının kıdemli Personal Trainer'ısın. 
            GÖREVİN: Kullanıcının kaldırdığı kiloları takip etmek ve gelişim analizi yapmaktır.
            KALORİ HESAPLAMA, sadece teknik performans ve gelişim yorumu yap.
            
            Kullanıcı Bilgileri:
            - Hedef: {user_profile['goal']}
            - Mevcut Kilo: {user_profile['weight']}kg
            
            {history_context}
            
            ADIMLAR:
            1. Metindeki egzersizleri ve kaldırılan kiloları (kg/set/tekrar) tespit et.
            2. Önceki antrenmanlarla kıyasla (varsa progressive overload tespiti yap).
            3. Teknik form, dinlenme ve gelişim odaklı profesyonel bir yorum yap.
            
            JSON FORMATI DÖN:
            {{
                "exercises": [
                    {{"name": "Bench Press", "weight": 60, "sets": 3, "reps": 10}}
                ],
                "feedback": "Geçen haftaya göre Bench Press'te 5kg artış görüyorum, bu harika! Formunu korumaya odaklan..."
            }}
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Bugünkü antrenmanım: {workout_text}"}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"Error analyzing workout: {str(e)}")
            return None

    def generate_weekly_fitness_report(self, user_profile, weekly_stats):
        """
        Generates a professional weekly summary of fitness performance.
        """
        try:
            stats_context = "Son 7 günlük egzersiz verileri:\n"
            for ex, data in weekly_stats.items():
                stats_context += f"- {ex}: Toplam Hacim {data['total_volume']}kg, Max Ağırlık {data['max_weight']}kg\n"

            prompt = f"""
            Sen NutriTrack Baş Antrenörüsün. Kullanıcının haftalık performansını yorumla.
            HEDEF: {user_profile['goal']}.
            
            {stats_context}
            
            GÖREVİN: 
            1. Haftalık genel bir değerlendirme yap.
            2. En çok gelişim gösterilen veya en çok çalışılan bölgeleri/hareketleri belirt.
            3. Gelecek hafta için 1-2 somut tavsiye ver.
            Cevabın profesyonel, kısa (max 4-5 cümle) ve ilham verici olsun.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Haftalık rapor oluşturulamadı: {str(e)}"

    def generate_fridge_recipe(self, user_profile, ingredients):
        """
        Generates a recipe based on available ingredients and user goals.
        """
        try:
            system_prompt = f"""
            Sen NutriTrack Akıllı Mutfak Şefisin. 
            Kullanıcının hedefi: {user_profile['goal']}.
            
            GÖREVİN: Kullanıcının elindeki malzemeleri kullanarak, hedefine uygun, sağlıklı ve pratik bir yemek tarifi üretmek.
            
            ADIMLAR:
            1. Malzemeleri analiz et.
            2. Hazırlanışı kısa ve net adımlarla anlat.
            3. Tarifin yaklaşık kalori ve makro değerlerini (protein, karb, yağ) belirt.
            4. Eğer malzemeler çok uyumsuzsa, en yakın sağlıklı alternatifi öner.
            
            Yanıtın profesyonel, iştah açıcı ve motive edici olsun.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Elimdeki malzemeler: {ingredients}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Tarif oluşturulamadı: {str(e)}"

    def generate_daily_briefing(self, user_profile, yesterday_stats):
        """
        Generates a proactive morning briefing based on yesterday's performance.
        """
        try:
            prompt = f"""
            Sen NutriTrack AI Baş Koçusun. Kullanıcıya özel 'Günün Savaş Planı'nı hazırla.
            HEDEF: {user_profile['goal']}.
            DÜNÜN ÖZETİ: {yesterday_stats['calories']} kcal, {yesterday_stats['protein']}g protein.
            
            GÖREVİN: 
            1. Dünü kısaca yorumla (iyi veya kötü).
            2. Bugünkü beslenme ve antrenman için 1 stratejik tavsiye ver.
            3. Motive edici, sert ama samimi bir kapanış yap.
            Yanıtın çok kısa (3 cümle) ve vurucu olsun.
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "Bugün hedeflerine odaklan, başarabilirsin!"

    def generate_shopping_list(self, user_profile, weekly_stats):
        """
        Generates a shopping list based on performance and goals.
        """
        try:
            stats_context = "Son haftalık hacim: " + str(weekly_stats.get('total_volume', 0))
            prompt = f"""
            Sen NutriTrack Alışveriş Asistanısın. 
            HEDEF: {user_profile['goal']}.
            {stats_context}
            
            Kullanıcının hedefine en uygun 5-7 maddelik bir market alışveriş listesi hazırla.
            Neden her birini alması gerektiğini 1-2 kelimeyle açıkla (Örn: Yumurta - Yüksek Protein).
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "Alışveriş listesi şu an hazırlanamadı."
