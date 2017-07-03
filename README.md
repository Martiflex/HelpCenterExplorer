#### Zendesk HC organization

```
Home page
    Category 1
        Section 1a
            Article 1a i)
            Article 1a ii)
            ...
        Section 1b
        ...
    Category 2
        Section 2a
            Article 2a i)
        Section 2b
            Article 2b i)
            Article 2b ii)
        Section 2c
        ...
```

#### Usage

```
git clone git@github.com:Martiflex/HelpCenterExplorer.git
cd HelpCenterExplorer
python crawler.py # you need python packages requests and datadog installed
python explorers/XXX.py
```

`python crawler.py` will crawl the whole HelpCenter setup in `configuration.py` as an object of the HomePage(HelpCenterElement) class defined in crawler.py and will save it in HC.Pickle. Running such a crawl may take several minutes.

`python explorers/XXX.py` will quickly load the HelpCenter saved in HC.Pickle and apply run script XXX to it.
*explorers/XXX.py* scripts are importing functions (and the HelpCenter object) from *explorer.py*.

#### Contribute

- There are already several scripts in the explorers folder. Feel free to add yours.
- Any improvement to the core (crawler.py, explorer.py, configuration.py), the organization of the project or tests are welcome through pull requests.
