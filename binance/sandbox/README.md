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

```bash
# Container içinde çalıştır
uv add nautilus_trader

# Test et
uv run python -c "import nautilus_trader; print('Nautilus Trader kurulumu başarılı!')"
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
