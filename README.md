Card maker
----------

A tool which allows you to generate fast prototype of cards to be used for

* [Tabletop Simulator](https://store.steampowered.com/app/286160/Tabletop_Simulator/)
* [Tabletopia](https://tabletopia.com/workshop/)
* Printing PDF


## Using the library

```
pip install git+https://github.com/dat-boris/card_maker#egg=playtest_card
```

And then you can reference in your code

```
import playtest_cards as pc

# Require you to setup your gsheet access token
csv_data = pc.read_gsheet(CSV_LINK, sheet_name=SHEET_NAME)

render_all(
    csv_data,
    asset_folder,  # Assets folder (where template will reference)
    asset_folder,
    # Different default layouts
    dimensions=pc.Layout.letter_landscape,
    #dimensions=pc.Layout.tabletopia_card,
    output_ext="pdf",  # can output as various formats
)
```


## Getting started

> Note the script is currently broken

The game starts with creating a manifest folder, which contains the
different specification of cards.  For example, if we want to create a
game of `game_checkers` - we would run the following:

```
./card_maker.py create game_checkers
```

This will create the sub-folder under `game_checkers` with two files:

* `layout.html.jinja` - a layout html which is used to generate the
  required file.
* `content.yaml` - a yaml file which contains the card variable which are
  where content is taken and put into above template.

To create the card, run:

```
./card_maker.py render content.yaml
```

Which will render the output file in `output.png` for printing.


# Adjusting layout

To use within [Tabletop Simulator](https://store.steampowered.com/app/286160/Tabletop_Simulator/),
you can use the following:

```
./card_maker.py render --layout tts content.yaml
```

And in tabletop simulator, upload the iamge and use 9 * 6 as the card dimension.


# Rendering from Google sheet

> Experimental feature

You can also pull in data from google sheet.

Check options from:

```
./card_maker.py render_from_gsheet --help
```

An example command:

```
pipenv run ./card_maker.py render -s <sheet name> \
                             --output rps-moves "<google sheet id>"
```
