Card maker
----------

A tool which allows you to generate fast prototype of cards to be used for
both [Tabletop Simulator](https://store.steampowered.com/app/286160/Tabletop_Simulator/)
as well as for printing.

## Getting started

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
./card_maker.py render
```

Which will render the output file in `output.png` for printing.
