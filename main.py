from anki.collection import Collection
import csv

col = Collection("/home/andrewcarterhughes/.local/share/Anki2/Andrew/collection.anki2")
notes = col.find_notes("deck:LRZTP::17")

def clean(str):
    return str.replace('&nbsp;', '').strip()

with open('out.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for note in notes:
        note_obj = col.get_note(note)
        print(note_obj['Front'])
        writer.writerow([clean(note_obj['Front']), clean(note_obj['Back'])])
col.close()