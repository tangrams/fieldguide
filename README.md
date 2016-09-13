![](imgs/00.gif)

# FieldGuide

Given a Valhalla route request construct a PDF using [Paparazzi's static maps](https://github.com/tangrams/paparazzi) ready to be send to a PaperWhite Kindle through their own [email-to-kindle service](https://www.amazon.com/gp/sendtokindle/email)

## Installation

### Install Paparazzi

You need to install [Tangram Paparazzi](https://github.com/tangrams/paparazzi) server in an [Amazon G2 GPU server](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using_cluster_computing.html). Paparazzi is a headless version of [Tangram-es](https://github.com/tangrams/tangram-es), to make static maps on the cloud. In that repository you kind find more details about the installation.

Then you need to modify `PAPARAZZI_SERVER` on `src/server.py` to point to the URL address of the paparazzi server.

### Install FieldGuide

Clone the repository and run the install script:

```bash
git clone https://github.com/tangrams/fieldguide.git
cd fieldguide
./fieldguide.sh install
```

and then FieldPapers:

```bash
./fieldguide.sh start
```

## Thanks to

- [Hanbyul](https://twitter.com/hanbyul_here) is responsable for the awesome interactive website that puts together [Tangram](https://mapzen.com/products/tangram/) + [Mapzen Search](https://mapzen.com/products/search/?lng=-73.98073&lat=40.72606&zoom=12) + [Mapzen Turn-by-Turn](https://mapzen.com/products/turn-by-turn/?d=0&lat=40.7259&lng=-73.9805&z=12&c=multimodal&st_lat=37.839682&st_lng=-122.485284&st=Vista%20Point&end_lat=37.80927&end_lng=-122.25981&end=Fairyland&use_bus=0.5&use_rail=0.6&use_transfers=0.4&dt=2016-09-20T08%3A00&dt_type=1) in a single [map here](https://github.com/mapzen/lrm-mapzen)

- [Geraldine Sarmiento](https://twitter.com/sensescape) is responsable for the beatiful and minimalistic [Refill Style for tangram maps](https://github.com/tangrams/refill-style)

- [Matt Blair](https://twitter.com/matteblair), [Varun Talwar](https://twitter.com/tallytalwar), [Karim Naaji](https://twitter.com/karimnaaji) and [Hannes Janetzek](https://twitter.com/hjanetzek) are responsable for [Tangram-es](https://github.com/tangrams/tangram-es) which esentially [Tangram Paparazzi](https://github.com/tangrams/paparazzi) is based on.