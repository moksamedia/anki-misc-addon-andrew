import re
from bs4 import BeautifulSoup
from aqt import gui_hooks
from anki import hooks

def prepare(html, card, context):

    pattern = r'([\u0F00-\u0FFF]+)'

    replacement = r'<span class="tibetan">\1</span>'
    new_html = re.sub(pattern, replacement, html)

    return new_html

def displaymatch(match):
    if match is None:
        return None
    return '<Match: %r, groups=%r>' % (match.group(), match.groups())

def prepare2(html, card, context):

    pattern = r"\"[^\"]+\"|([\u0F00-\u0FFF]+)"
    def replace_func(match):
        print("match="+displaymatch(match))
        if match.group(1) is None:
            return match.group()
        return r'<span class="tibetan">'+match.group()+'</span>'

    new_html = re.sub(pattern, replace_func, html)
    return new_html

gui_hooks.card_will_show.append(prepare2)

import csv

from anki.exporting import Exporter
from anki.hooks import addHook
from anki.lang import _
from anki.utils import  ids2str, splitFields
from anki.collection import Collection
from anki.collection import DeckIdLimit, NoteIdsLimit
from io import BufferedWriter

from aqt.import_export.exporting import Exporter as ExporterGui

class CSVNoteExporter(Exporter):

    extension = ".csv"
    key = "Notes in CSV"
    includeID = False
    includeTags = False
    includeHtml = False
    db_query = """
select guid, flds, tags from notes
where id in
(select nid from cards
where cards.id in %s)
    """

    def __init__(self, col) -> None:
        Exporter.__init__(self, col)
        self.includeID = False

    def doExport(self, file) -> None:
        writer = csv.writer(file)
        cardIds = self.cardIds()
        self.count = 0
        for _id, flds, tags in self.col.db.execute(self.db_query % ids2str(cardIds)):
            row = []
            # note id
            if self.includeID:
                row.append(str(_id))
            # fields
            row.extend([self.escapeText(f) for f in splitFields(flds)])
            # tags
            if self.includeTags:
                row.append(tags.strip())
            self.count += 1
            writer.writerow([x.encode("utf-8") for x in row])

def _id(obj):
    return ("%s (*%s)" % (obj.key, obj.extension), obj)

def update_exporters_list(exps):
    exps.append(_id(CSVNoteExporter))

#hooks.exporters_list_created.append(update_exporters_list)

class CSVNoteExporterGui(ExporterGui):

    extension = "csv"
    show_deck_list = True
    show_include_html = False
    show_include_tags = False
    show_include_deck = False
    show_include_notetype = False
    show_include_guid = False

    @staticmethod
    def name() -> str:
        return "Export Notes to CSV"

    def export(self, mw, options) -> None:
        options = gui_hooks.exporter_will_export(options, self)

        def on_success(count: int) -> None:
            gui_hooks.exporter_did_export(options, self)
            tooltip(tr.exporting_note_exported(count=count), parent=mw)

        print("options="+str(options))
        print("options.limit="+str(options.limit))

        if (type(options.limit) is DeckIdLimit):
            deckId = str(options.limit.deck_id)
            print("deckId="+deckId)
            deck = mw.col.decks.get(deckId)
            print(str(deck))
            deckName = deck['name']
            notes = mw.col.find_notes("deck:"+deckName)
        else:
            noteIds = options.limit.note_ids
            print("noteIds="+str(noteIds))
            notes = noteIds

        print("notes="+str(notes))

        def clean(str):
            return str.replace('&nbsp;', '').strip()

        with open(options.out_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for note in notes:
                note_obj = mw.col.get_note(note)
                front = clean(note_obj['Front'])
                frontAlt = clean(note_obj['Front_alt'])
                back = clean(note_obj['Back'])
                if frontAlt:
                    back = " // ".join([back, frontAlt])
                print(str([front, back]))
                writer.writerow([front, back])

def update_exporters_list_gui(exps):
    exps.append(CSVNoteExporterGui)

gui_hooks.exporters_list_did_initialize.append(update_exporters_list_gui)
