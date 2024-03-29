<h1><span style="color: green;">Public</span> <span style="color: #0000a2;">Spending</span> <span style="color: #e2e200;">Analisys</span></h1>
Project focused on analyzing Brazilian Corporate Spendings to identify and detect anomalies within corporate credit cards financial transactions.

## Development Preview
- [Zeit](https://zeit.co/)

## Docker

### Docker Playground
https://labs.play-with-docker.com/

### Fast Deploy

#### Windows
Utilize apenas o *build.cmd* localizado na raiz do projeto:

```bash
build
```

#### Linux / MacOS
Utilize o *build.sh* localizado na raiz do projeto:

```bash
$ bash build.sh
```

### Manual Deploy

Build Image:

```bash
docker build -t public-spending-api .
```

Run Container:

```bash
docker run --rm -p 5000:5000 --name pub-spend-api public-spending-api
```

Access Website:

http://localhost:5000/

Stop Container:

```bash
docker stop pub-spend-api
```


## References
- [Portal da transparência API](http://transparencia.gov.br/swagger-ui.html#!/Gastos32por32meio32de32cart227o32de32pagamento/cartaoUsingGET)
- [Isolation Forest](https://en.wikipedia.org/wiki/Isolation_forest)
- [Anomaly Detection](https://en.wikipedia.org/wiki/Anomaly_detection)
- [Unsupervised Anomaly Detection with Isolation Forest](https://www.youtube.com/watch?v=5p8B2Ikcw-k)
- [Outlier Detection With Isolation Forest](https://towardsdatascience.com/outlier-detection-with-isolation-forest-3d190448d45e)
- [Scikit Learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Jinja2 documentation](https://jinja.palletsprojects.com/en/2.9.x/templates/#with-statement)
- [Outlier Detection with Extended Isolation Forest](https://towardsdatascience.com/outlier-detection-with-extended-isolation-forest-1e248a3fe97b)
- [Extended Isolation Forest (EIF) on GitHub](https://github.com/sahandha/eif)
