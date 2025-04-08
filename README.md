## 📌 LegalDocsCrawler

LegalDocsCrawler é um web scraper que automatiza a busca e o download de documentos jurídicos do site [BAILII](https://www.bailii.org/), focando em casos relacionados a **tráfico humano, trabalho forçado e escravidão moderna**. O programa utiliza Selenium para navegar na página e Requests para baixar arquivos PDF, convertendo-os posteriormente para texto e CSV para facilitar a análise de dados.

## 🚀 Funcionalidades

- 🔍 **Pesquisa automática** de casos jurídicos no BAILII com termos específicos.
- 📥 **Download e armazenamento** de decisões judiciais em formato PDF.
- 📝 **Conversão de PDFs** para arquivos TXT.
- 📊 **Conversão de arquivos TXT** para CSV para análise estruturada.
- 🔄 **Suporte a múltiplas páginas** de resultados com navegação automática.

## 🔧 Tecnologias Utilizadas

- **Python** 🐍  
- **Selenium** (Automação de navegador)  
- **Requests** (Download de arquivos)  
- **Pandas** (Manipulação de dados)  
- **PyPDF2** (Extração de texto de PDFs)  

## 📦 Instalação

1️⃣ Clone este repositório:

```bash
git clone https://github.com/seu-usuario/LegalDocsCrawler.git
cd LegalDocsCrawler
```

2️⃣ Crie um ambiente virtual e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3️⃣ Instale o Poppler (dependência de sistema)

O Poppler é utilizado para converter arquivos PDF em TXT e não é gerenciado pelo pip. Siga as instruções abaixo conforme seu sistema operacional:

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get install poppler-utils
```

**macOS (usando Homebrew):**

```bash
brew install poppler
```

**Windows:**

Faça o download do Poppler for Windows.

Extraia o conteúdo em uma pasta e adicione o diretório bin do Poppler à variável de ambiente PATH.

4️⃣ Execute o scraper:

```bash
python main.py
```

## 🛠️ Como Funciona

1. O script acessa o site BAILII e realiza uma busca avançada usando palavras-chave.
2. Ele navega pelos resultados, abrindo cada caso em uma nova aba.
3. Se um PDF estiver disponível, ele será baixado e salvo localmente.
4. O programa converte os PDFs para arquivos TXT e, em seguida, para CSV.

## 📌 Estrutura do Projeto

```
LegalDocsCrawler/
│── cases/               # PDFs baixados
│── text_cases/          # Arquivos TXT extraídos dos PDFs
│── csv_cases/           # Arquivos CSV gerados
│── main.py              # Script principal
│── pdf_to_txt.py        # Conversão de PDF para TXT
│── txt_to_csv.py        # Conversão de TXT para CSV
│── requirements.txt     # Dependências do projeto
└── README.md            # Documentação
```

## 📄 Licença

Este projeto está licenciado sob a **MIT License** – veja o arquivo [LICENSE](LICENSE) para mais detalhes.
