# 🔧 Sistem Optimizasyon Notları

## Redis Uyarıları ve Çözümleri

Bu dokümantasyon, Nautilus Trader Docker ortamında karşılaşabileceğiniz sistem uyarıları ve çözümlerini içerir.

### 1. Memory Overcommit Uyarısı

**Uyarı:**
```
WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition.
```

**Açıklama:** 
Bu uyarı, sistem bellek yönetimi ile ilgilidir. Redis'in arka plan kaydetme işlemleri için gereklidir.

**Çözümler:**

#### Docker Host'ta Kalıcı Çözüm:
```bash
# Linux sistemlerde:
sudo sysctl vm.overcommit_memory=1
echo 'vm.overcommit_memory = 1' | sudo tee -a /etc/sysctl.conf

# macOS'ta (gerekli değil, sadece Linux):
# Bu ayar macOS'ta geçerli değildir
```

#### Docker Compose Seviyesinde:
Docker-compose.yml dosyamızda sistemik ayarlar ekledik:
```yaml
sysctls:
  - net.core.somaxconn=1024
```

### 2. Clocksource Uyarısı

**Uyarı:**
```
WARNING Your system is configured to use the 'xen' clocksource which might lead to degraded performance.
```

**Açıklama:** 
Bu uyarı, özellikle sanal makinelerde (AWS, GCP, Azure) görülür ve clock source'un optimizasyonu ile ilgilidir.

**Çözümler:**

#### Cloud Ortamlarında:
- Bu uyarı çoğunlukla zararsızdır
- Performans testleri yaparak gerçek etkiyi ölçebilirsiniz
- Gerekirse cloud sağlayıcının optimize edilmiş instance türlerini kullanın

#### Lokal Geliştirme:
```bash
# Clock source'u kontrol et:
cat /sys/devices/system/clocksource/clocksource0/current_clocksource

# Mevcut clock source'ları listele:
cat /sys/devices/system/clocksource/clocksource0/available_clocksource
```

### 3. Uygulanan Optimizasyonlar

#### Redis Konfigürasyonu:
- `redis.conf` dosyası eklendi
- Memory policy: `allkeys-lru`
- Persistence: AOF + RDB hybrid
- Network optimizasyonları

#### Container Optimizasyonları:
- `entrypoint.sh` script'i eklendi
- Sistem parametrelerinin otomatik ayarlanması
- Log seviyelerinin optimize edilmesi

#### Docker Compose Optimizasyonları:
- Sysctls ayarları
- Health check'ler
- Resource limits

### 4. Performans İzleme

Redis performansını izlemek için:

```bash
# Redis içine bağlan:
docker exec -it nautilus-redis redis-cli

# Info komutları:
INFO memory
INFO persistence
INFO replication
INFO stats

# Slow query log:
SLOWLOG GET 10

# Memory usage:
MEMORY USAGE keyname
```

### 5. Production Önerileri

#### Sistem Seviyesi:
```bash
# Memory overcommit
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf

# Network
echo 'net.core.somaxconn = 1024' >> /etc/sysctl.conf

# Kernel parametreleri yükle
sysctl -p
```

#### Docker Seviyesi:
```yaml
# docker-compose.yml'de resource limits:
services:
  nautilus-redis:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### 6. Troubleshooting

#### Redis Bağlantı Problemleri:
```bash
# Redis'e bağlanabilir mi kontrol et:
docker exec nautilus-redis redis-cli ping

# Network connectivity:
docker exec nautilus-sandbox-trader ping nautilus-redis

# Log kontrolü:
docker logs nautilus-redis --tail 50
```

#### Memory İzleme:
```bash
# Container memory kullanımı:
docker stats nautilus-redis

# Redis memory info:
docker exec nautilus-redis redis-cli INFO memory
```

### 7. Notlar

- Bu uyarılar çoğunlukla performance hintleridir, kritik hatalar değil
- Development ortamında güvenle göz ardı edilebilir
- Production ortamında sistem yöneticisi ile koordine edilmelidir
- Docker Desktop (macOS/Windows) ortamında bazı kernel ayarları mevcut değildir

---

**💡 İpucu:** Eğer uyarılar performansı etkiliyorsa, Redis'in `MONITOR` komutunu kullanarak gerçek zamanlı komut akışını izleyebilirsiniz:

```bash
docker exec -it nautilus-redis redis-cli MONITOR
```
