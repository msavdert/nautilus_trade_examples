# 🌊 Nautilus Trader - Professional Trading Framework

[![License](https://img.shields.io/badge/license-LGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)

**Professional algorithmic trading framework with multiple environment support.**

> 🇹🇷 **Türkçe dokümantasyon için**: [README.tr.md](README.tr.md)

---

## 📁 Project Structure

```
nautilus_trade/
├── README.md                   # This overview (English)
├── README.tr.md               # Turkish overview
├── sandbox/                   # 🧪 Safe testing environment
│   ├── README.md             #    Complete sandbox documentation (English)
│   ├── README.tr.md          #    Complete sandbox documentation (Turkish)
│   ├── docker-compose.yml    #    Sandbox deployment
│   ├── sandbox_trader.py     #    Trading bot implementation
│   ├── .env                  #    Environment variables
│   ├── Dockerfile            #    Container configuration
│   └── requirements.txt      #    Python dependencies
└── live/                     # 🔴 Live trading environment
    └── (future implementation)
```

---

## 🧪 Sandbox Environment

The **sandbox** environment provides a completely safe testing environment using Binance Testnet:

- **Safe Testing**: Uses virtual money, no real funds at risk
- **Real Market Data**: Live data from Binance Testnet
- **Professional Architecture**: PostgreSQL + Redis + Nautilus Trader
- **EMA Cross Strategy**: Proven algorithmic trading strategy
- **Docker Containerized**: One-command deployment
- **Comprehensive Documentation**: Detailed setup and usage guide

**👉 Get started with sandbox trading:**

```bash
cd sandbox/
# Follow the detailed README.md in sandbox directory
```

---

## 🔴 Live Environment

The **live** environment is designed for real trading with actual funds:

⚠️ **WARNING: Live trading involves real money and substantial risk!**

- **Real Trading**: Uses live exchange APIs with real funds
- **Production Architecture**: Scalable, monitored, backed up
- **Advanced Risk Management**: Enhanced safety controls
- **Regulatory Compliance**: Meets trading regulations
- **Professional Monitoring**: Real-time alerts and dashboards

**🚧 Status: Under Development**

The live environment is currently under development. For now, please use the sandbox environment for testing and development.

---

## 🚀 Quick Start

### For Sandbox Testing

```bash
# 1. Navigate to sandbox
cd sandbox/

# 2. Follow the complete setup guide
cat README.md

# 3. Quick start (requires .env setup)
docker-compose up -d
```

### For Development

```bash
# 1. Clone repository
git clone <repository-url>
cd nautilus_trade

# 2. Choose your environment
cd sandbox/     # For safe testing
# cd live/      # For real trading (future)

# 3. Follow environment-specific documentation
```

---

## 🛠️ Development Philosophy

This project follows a **multi-environment approach**:

1. **Sandbox First**: Always test in sandbox before live trading
2. **Manual Control**: No automatic scripts - you control everything
3. **Transparent Configuration**: All settings visible and configurable
4. **Professional Architecture**: Production-ready from day one
5. **Safety First**: Multiple layers of protection and validation

---

## 📚 Documentation

### Complete Guides

- **📖 Sandbox Guide**: `sandbox/README.md` - Complete sandbox documentation
- **🔧 API Reference**: [Nautilus Trader Docs](https://docs.nautilustrader.io/)
- **📊 Strategy Development**: Examples and tutorials in sandbox
- **🔒 Security Guide**: Best practices for safe trading

### Quick References

- **Docker Commands**: `docker-compose up/down/logs`
- **Environment Setup**: `.env` file configuration
- **Log Monitoring**: Real-time system monitoring
- **Troubleshooting**: Common issues and solutions

---

## 🤝 Contributing

We welcome contributions to both sandbox and live environments:

1. **Start with Sandbox**: Test your changes in sandbox first
2. **Follow Architecture**: Maintain separation between environments
3. **Add Documentation**: Update relevant README files
4. **Test Thoroughly**: Ensure changes work in Docker containers
5. **Security Review**: Consider security implications

---

## ⚠️ Important Notes

- **Always Start with Sandbox**: Never begin with live trading
- **Manual Operation**: This system requires manual setup and monitoring
- **Risk Management**: You are responsible for all trading decisions
- **No Automation**: No automatic scripts - manual control only
- **Educational Purpose**: Primarily for learning algorithmic trading

---

## 📄 License

This project is licensed under the LGPL-3.0 License.

---

## 🚀 Get Started

**Ready to start algorithmic trading?**

```bash
cd sandbox/
cat README.md  # Read the complete guide
```

**Happy Trading!** 📈🌊
