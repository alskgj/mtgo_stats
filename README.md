MTGO Results Tracker
====================
Fetches all pioneer tournaments published on mtgo.com and calculates the win and playrate.

### Sample Output

```
$ python cli.py stats --deck "Rakdos Vampires" --card "Archfiend of the Dross"
#  Deck                                          PR%    WR%    95% CI: [L, U]    #matches
=========================================================================================
1  Rakdos Vampires (3x Archfiend of the Dross)   10.07  54.6   [52.82%, 56.38%]  663
2  Rakdos Vampires (0x Archfiend of the Dross)   9.51   50.67  [48.76%, 52.57%]  600
3  Rakdos Vampires (2x Archfiend of the Dross)   2.29   53.75  [50.5 %, 57.0 %]  160
4  Rakdos Vampires (1x Archfiend of the Dross)   0.35   50.0   [40.07%, 59.93%]  24
5  Rakdos Vampires (4x Archfiend of the Dross)   0.28   31.25  [19.55%, 42.95%]  16          
```


```
$ python cli.py stats
#  Deck                  PR%    WR%    95% CI: [L, U]    #matches
=================================================================
1  Rakdos Vampires       22.5   52.56  [51.36%, 53.76%]  1463
2  Izzet Phoenix         16.46  51.36  [49.95%, 52.77%]  1141
3  Amalia Combo          9.31   49.05  [47.34%, 50.76%]  630
4  Waste Not             7.78   50.36  [48.47%, 52.25%]  552
5  Bring to Light        6.6    49.55  [47.35%, 51.74%]  440
6  Lotus Field           6.88   43.56  [41.27%, 45.85%]  427
7  Spirits               4.51   51.12  [48.91%, 53.33%]  356
8  Transmogrify          3.82   52.65  [49.48%, 55.83%]  264
9  UW Control            3.68   48.05  [45.13%, 50.97%]  256
10 Boros Heroic          3.33   48.61  [45.37%, 51.85%]  216
```
