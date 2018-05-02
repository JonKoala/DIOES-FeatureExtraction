# diariobot-datamining
Ferramenta para extração de informações dos artigos obtidos pelo [diariobot-scraper](https://github.com/JonKoala/diariobot-scraper).

### Requisitos
 - [Python](https://www.python.org/) >= 3.6
   - [NLTK](https://www.nltk.org/)
   - [NumPy](http://www.numpy.org/)
   - [PyYAML](http://pyyaml.org/wiki/PyYAML)
   - [scikit-learn](http://scikit-learn.org/)
   - [SQLAlchemy](https://www.sqlalchemy.org/)
 - Database SQL Server 2014

### Configuração
O projeto depende de um arquivo `appconfig.yml`, na sua raiz, contendo algumas configurações locais. Crie uma cópia do arquivo `appconfig.yml.example` e coloque as configurações do seu ambiente.

Exemplo de `appconfig.yml`:
``` yaml
db:
  connectionstring: '[My PyODBC connection string]'

classifier:
  classes: ['CLASSE-A', 'CLASSE-B']
  tipos_publicacoes: ['TIPO-1', 'TIPO-2']
  num_keywords: 15

tuning:
  cv_num_splits: 3
  params_filepath: '[TUNING RESULTS PATH]'

logging:
  filepath: '[LOGFILE PATH]'
  filehandler:
    backupCount: 0
    maxBytes: 0
```
Note que o valor informado para a `connectionstring` deve seguir o padrão do [PyODBC](http://docs.sqlalchemy.org/en/latest/dialects/mssql.html#pass-through-exact-pyodbc-string).

### Execução
Essa ferramenta usa os artigos obtidos através do [scraper](https://github.com/JonKoala/diariobot-scraper) e classificados manualmente através da aplicação web do diariobot (o [crowdsourcer](https://github.com/JonKoala/diariobot-webapp-client#execu%C3%A7%C3%A3o)) para treinar um classificador de artigos do Diário Oficial.

Para treinar um classificador novo e classificar os artigos armazenados no banco de dados, execute o script `routine_predict.py`. Esse script classifica apenas artigos ainda não classificados na base de dados, para aplicar o classificador na base inteira, execute o comando adicionando o parâmetro `--full`.
``` bash
python routine_predict.py
```
Ao final da execução, o script deve salvar os resultados no banco de dados.

Para extrair padrões identificados através de expressão regular (atualmente apenas valores monetários), execute o script `routine_extract_patterns.py`.
``` bash
python routine_extract_patterns.py
```
É possível também avaliar o classificador e testar os parâmetros usados em cada etapa da rotina de criação de classificadores. Para identificar os melhores parâmetros para usar na criação de um classificador, execute o script `routine_tune_predictor.py`.
``` bash
python routine_tune_predictor.py
```
Ao final da execução, o script deve exibir um relatório com os melhores parâmetros encontrados e uma avaliação detalhada do desempenho do classificador. Os melhores parâmetros encontrados são salvos em um arquivo _json_, no caminho especificado no arquivo de configurações.
