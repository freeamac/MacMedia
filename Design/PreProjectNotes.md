
# Notes:

- Deletions will need to be confirmed.
- How to handle deletions after data is already in the catalog? Should you use a
  special delete mechanism or should you be put into the input editor with
  the fields already pre-populated with deletion as an option?
- You can either open new or existing catalog.
- Global save flag.
-  Should also periodically write out temp copies of modified catalog.
- Need to check the consistency of changes. For example, if I change the
  artist of a song, it could introduce an inconsistency as this song
  will be listed on albums by a different artist.
- For displays perhaps a tree browser based display would be best. You could
  explode out into songs. Properties listed could be the artist and dates.
- If I can separate the UI from the rest of the logic, I will be able to
  create different "skins" as long as all skins write to the api of the logic.

---
# Use Cases

## Use Cases Questions:

- Does the search collection use case effectively handle searching
  for artists or songs? How about the display list which currently
  appears to be album-centric?


## Case #1:

- User starts the application to delete a Compact Disc.
- First they must select the music catalog to use.
- Next, the user must interact with the application to search for the Compact Disk. 
- Once the CD is located, the user selects it for deletion.

## Case #2:

- User starts the application to delete a song in a Compact Disc listing.
- First they must select the music catalog to use.
- Next, the user must interact with the application to search for the Compact Disc. 
- Once the CD is located, the user selects a song on the CD for deletion.

## Case #3:

- User starts the application to change title of a Compact Disc.
- First they must select the music catalog to use.
- Next, the user must interact with the application to search for the  Compact Disc. 
- Once the CD is located, the updates the CD title.

## Case #4:

- User starts the application to change the title of a song of a Compact Disc.
- First they must select the music catalog to use.
- Next the user must interact with the application to search for the  Compact Disc. 
- Once the CD is located, the user selects the song updates it's title.

## Case #5:

- User starts the application to add a Compact Disc.
- First they must select the music catalog to use.
- Next the user must interact with the application to add the CD and all its songs.

## Case #6:

- User starts the application to change the artist of a song.
- First they must select the music catalog to use.
- Next the user must interact with the application to search for the song.
- Once they locate the song, the user changes the artist.

## Case #7:

- User starts the application to display all Compact Discs.
- First they must select the music catalog to use.
- Next, the user interacts with the application to display all Compact Discs.

## Case #8:

- User starts the application to display all songs by a particular artist.
- First they must select the music catalog to use.
- Next the user interacts with the application to search for the artist. 
- Once the artist is located, all their songs are displayed.

## Case #9: 

- User starts the application to display all Compact Discs by a particular artist.
- First they must select the music catalog to use.
- Next the user interacts with the application to search for the artist. 
- Once the artist is located, all their CDs are displayed.
