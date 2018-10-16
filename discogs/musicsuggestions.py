import discogs_client
import requests
import lxml.html
import numpy as np


artist1 = input("Artist 1?")
artist2 = input("Artist 2?")

# assigns artists to their discogs artist id via discogs API
# note: this is no longer a working token, generate your own on Discogs>Developer Settings
d = discogs_client.Client('ExampleApplication/0.1', user_token="GGbMZRmjuLZktxPkXHVsHoyYShnLscJvwKFEnDae")
artist1id = d.search(artist1, type='artist')[0].id
artist2id = d.search(artist2, type='artist')[0].id


# returns text based on xpath location of css selector instances
def extract(el, css_sel):
    # finds xpath for el instance of css selector
    xpath = el.cssselect(css_sel)
    # returns the text at that xpath
    if len(xpath) != 1:
        return None
    else:
        return xpath[0].text


# returns a list of compilations that an artist was a part of
def get_comps(artistid):
    url = "https://www.discogs.com/artist/" + str(artistid) + \
          "?sort=year%2Casc&limit=25&subtype=Compilations&type=Appearances&page=1"
    r = requests.get(url, headers={'User-Agent': 'Anonymous'})
    # stores html from requests.get() string to root
    root = lxml.html.fromstring(r.text)
    comps = []

    # cycles through list of compilations and appends them to the comps array
    for row in root.cssselect("#artist tr"):
        id = row.get("data-object-id")
        comps.append(id)

    return comps


# cycles through a compilation and returns all artists on that compilation in an array
def get_artists(compid):
    url = "https://www.discogs.com/release/" + str(compid)
    r = requests.get(url, headers={'User-Agent': 'Anonymous'})
    root = lxml.html.fromstring(r.text)
    artists = []

    for row in root.cssselect(".playlist tr"):
        id = extract(row, ".tracklist_track_artists a")
        artists.append(id)

    return artists


# takes array of compilations by an artist, yields a set of all artists on each of those compilations
def setmaker(artistid):
    # comps is list of compilations
    comps = get_comps(artistid)
    # instantiates cumulative artist array for all comps
    artists = get_artists(comps[0])
    x = 1
    # cycle through comps and add each artist to the artist array
    while x < len(comps):
        artists = np.append(artists, get_artists(comps[x]))
        x += 1
    artists = set(artists)
    # sometimes the artists appear as a suggestion for themselves
    artists.discard(artist1)
    artists.discard(artist2)
    artists.discard('None')
    artists.discard(None)
    return artists


a = artist1id
b = artist2id
set_a = setmaker(a)
set_b = setmaker(b)
# third artist is possible, but it slows the program down and yields fewer results
# set_c = setmaker(c)
print(set_a & set_b)
