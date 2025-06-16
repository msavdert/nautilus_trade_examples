# Nautilus Trader Minimal Setup

Bu minimal setup sadece Redis ile çalışır ve PostgreSQL kullanmaz. GitHub'daki orijinal Nautilus Trader .docker yapısına uygun olarak oluşturulmuştur.

## Gereksinimler

Öncelikle Nautilus Trader repository'sini clone edin:

```bash
git clone https://github.com/nautechsystems/nautilus_trader.git
```

Bu repository'den ihtiyacınız olan dosyaları (uv.lock, pyproject.toml, vs.) bu dizine kopyalayabilirsiniz.

## Kullanım

### 1. Servisleri Başlatma

```bash
docker-compose up -d
```

### 2. İnteraktif Shell

```bash
docker-compose exec nautilus-trader bash
```

### 3. Nautilus Trader Kurulumu (Container içinde)

Container içinde trading projesi oluşturun ve Nautilus Trader'ı ekleyin:

```bash
# Container içinde çalıştır

# 1. YENİ PROJE OLUŞTUR (gerekli!)
uv init my-trading-project

# 2. PROJE DİZİNİNE GİR
cd my-trading-project

# 3. NAUTILUS TRADER EKLE
uv add nautilus_trader

# 4. KURULUMU TEST ET
uv run python -c "import nautilus_trader; print('Nautilus Trader kurulumu başarılı!')"
```

**ÖNEMLİ:** `uv add` komutunu kullanmadan önce mutlaka `uv init` ile proje oluşturmalısınız!

#### Alternatif: Tek Komutla

```bash
# Tek seferde proje oluştur + Nautilus Trader ekle
uv init trading-project && cd trading-project && uv add nautilus_trader
```

### 4. Servisleri Durdurma

```bash
docker-compose down
```

## Yapı

- **Redis**: Market data caching için
- **Nautilus Trader**: Ana trading engine (minimal kurulum)
- **Volumes**: Redis data persistence

## Notlar

- PostgreSQL dahil değildir (isteğiniz üzerine)
- Sadece Redis ile minimal bir kurulum
- Development için hazır
- Orijinal Nautilus .docker yapısına uygun

## Sonraki Adımlar

1. Nautilus repository'den gerekli dosyaları kopyalayın
2. Trading script'lerinizi ekleyin
3. İhtiyaçlarınıza göre genişletin

## Yaygın Hatalar ve Çözümleri

### ❌ Hata: `No pyproject.toml found`
```bash
uv add nautilus_trader
# error: No `pyproject.toml` found in current directory
```

**Çözüm:** Önce proje oluşturun
```bash
uv init my-project
cd my-project
uv add nautilus_trader
```

### ❌ Hata: Container'a bağlanamama
```bash
docker-compose exec nautilus-trader bash
# Error: No such container
```

**Çözüm:** Container'ın çalışıp çalışmadığını kontrol edin
```bash
docker-compose ps
docker-compose up -d  # Eğer çalışmıyorsa
```

### ✅ Doğru Adım Sırası
1. `docker-compose up -d` - Container'ları başlat
2. `docker exec -it nautilus-trader bash` - Container'a bağlan  
3. `uv init my-project` - Yeni proje oluştur
4. `cd my-project` - Proje dizinine gir
5. `uv add nautilus_trader` - Nautilus Trader ekle
6. `uv run python your_script.py` - Script çalıştır

### 💡 İpuçları

**Test Projeleri İçin:**
```bash
# Git sorunlarını önlemek için geçici test klasörü oluşturun
cd /tmp && uv init test-project && cd test-project
```

**Production Projeleri İçin:**
```bash
# Ana workspace'de gerçek projelerinizi oluşturun
cd /workspace && uv init my-trading-bot && cd my-trading-bot
```
