# MacMedia
MacMedia Media Library Tracker

# Development

A virtual environment should be set up with the imports defined in the *requirements.txt* file.
Additionally it is helpful to install `gunicorn` to run the Flask application under this
server to mimic the Azure deployed server environment.

## Developer Linting

[Flake8](https://flake8.pycqa.org/en/latest/) is utilized to enforce code style with a couple of 
flags turned off as defined in the *setup.cfg* file. Linting can be invoke as:
```
    make lint
```

## Developer Testing

[pytest](https://docs.pytest.org/en/7.1.x/) is utilized as the test runner for MacMedia test cases. Test
cases are defined under the *tests* directory. Data required for test cases is stored in *tests/data*.
Test case execution can be invoked as:
```
    make test
```

Additionally, [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) is utilized to generate test case
coverage statistics. The html report is stored under *apps/docs/htmlcov*. It can be invoked with a browser 
display of the results after running using:
```
    make coverage
```

If you just want a terminal text display of test case coverage, use the same target as used in the CI pipeline:
```
    make coverage-ci
```

## Running On Localhost

You can install a local Postgres server and connect to a development MacMedia database on PostgreSQL instance.
You need to define all of the following environment variables:

| Environment Variable | Purpose | Defatult |
|----------------------|---------|----------|
| DB_USER              | Database user privileged to access the MacMedia database | None |
| DB_PASSWORD          | The password of the database user accessing the MacMedia database | None |
| DB_HOST              | Host address | 127.0.0.1 |
| DB_PORT              | Port used to connect to the database | 5432 |
| DATABASE             | The name of the MacMedia database | None |

The default value of the connection string will be "127.0.0.1:5432", the localhost and default postgres port. Then to run:
```
    flask --app app/app.py run --debug
```



## Development Deployment Environment

For running the application, Docker containers are used. Docker Desktop should be installed and
configured to use WSL 2. For example, in this case, the configuration is for Ubuntu:
![Configure WSL 2 Docker](app/docs/static/docker_wsl_config.png)

The application can be built into a docker image using the included `Dockerfile`. The image can be created
and launched using the `Makefile` targets:
```
    make build
    make run-dev
```
The running application in the Docker container can then be accessed at the url __http://localhost:5000/main__.
`make run-dev` essentially runs the below which you could also run in a terminal:
```
    docker run -p 5000:5000 --env FLASK_ENV=development macmedia:latest
```

## Setting The Application Environment

The running environment and configuration is determined by the setting of the environment variable
*APP_ENV*. The default value is "Dev". The following settings equate to specific configurations:

| Value | Configuration Used | Database Used |
|-------|--------------------|---------------|
| "Test"  | Test runner | Local pre-loaded SQLite |
| "Dev"   | Development | Local pre-loaded SQLite unless over ridden as decribed above in "Running On Localhost"|
| "Staging" | Azure Staging | Azure persistant staging PostgreSQL database instance |
| "Production" | Azure Production | Azure persistant production PostgreSQL database instance |


## Github Workflows

Upon a push to master, linting, code style checking, code coverage (which invokes the test cases), and security issues
will all be checked. ![Bandit](https://bandit.readthedocs.io/en/latest/) is used to check for
security issues in the code.

---

# Documentation

Sphinx and reStructuredText are utilized to create developer originated documentation.
The __.rst__ files are located under the `app/docs` directory. A top level `Makefile` is
used to generate the documentation with the command:
```
    make docs
```
The root of the resulting html documentation is `app/docs/_build/html/index.html`.

---

# Music Media Schema

Music media is currently encoded in an html file. At the top level, each piece of music media
is enclosed in a set of tags. The top level tag contains metadata about the music media piece
and then one or more tracklists. The tracklist level contains metadata about the tracklist and
a list of song entries. The song entry level contains all the information about a particular
song.

## Top Music Media Level Container

The top level container is specified with a paragraph tag, \<p>\</p>. Within the tag is an
\<a rel="{media_type}"> tag which defines the type of music media in "media_type" and encases
all the information about this piece of music media. Required information, each of which is
enclosed in an \<h3>\</h3> tag, include the title of the music media piece, the artist(s) of the
music media piece, and the publication year of the music media piece. Optionally, there
may be a classical composer of the music media piece and/or a mixer of the music media piece. Finally
there will be one or more tracklists enclosed described in the next section.

The schema looks like:

```
<p>
<a rel="{media_type}>
<h3><a rel="title">{title}</a></h3>
<h3><a rel="artists">{artist}</a></h3>
<h3><a rel="date">{year}</a></h3>
<h3><a rel="classical-composer">{classical-composer}</a></h3>
<h3><a rel="mixer">{classical-composer}</a></h3>
             .
             .
             .
</a>
</p>
```

## Tracklist Level Container

In the case of a single tracklist, which generally occurs on a CD, there will just be an order list
of song entries as the tracklist contains no metadata. For multiple tracklists, each is contained
in a \<a rel="side"> tag. In this situation, a name for the track is manditory and there may
optionally be a mixer associated with that track. Each are contained in \<h4>\</h4> tags.

The schema for a single tracklist looks like:

```
<ol>
  .
  .
  .
</ol>
```

For multiple tracklists, each tracklist looks like:

```
<a rel="side">
<h4><blockquote>{tack_name}</blockquote></h4>
<h4>Mixed By <a rel="side-mixer>{side_mixer}</a></h4>
<ol>
  .
  .
  .
</ol> 
</a>
```

## Song Entry Level Container

As the song entries occur inside the order list of the tracklist container, the song metadata
for each song entry is enclosed in a \<li>\</li> tag. All song metadata is specified by anchor
tags (\<a rel="{song_metadata_specifier}">) and additional specific formatting. The only
manditory piece of metadata required is the song name. The list of potential additional
song metadata include:
* song artist(s)
* song mix
* song date (year)
* song country of origin  
* classical work the song is from
* classical composer of the song
* movie or show song featured in
* parts of the song
The parts of the song is an order list container of each part.

The schema for a single song entry looks like:

```
  <li><a rel="song">{song_name}</a><br>
      <b><a rel="song-artist">{song_artist}</a></b><br>
      (<a rel="song-mix">{song_mix}</a>)<br>
      from <i><a rel="song-classical-work">{song_classical_work}</a></i><br>
      by <b><a rel="song-classical-composer">{song_classical_composer}</a></b><br>
      (featured in <a rel="song-featured-in">{movie_or_show}</a>)<br>
      - <a rel="song-date">{year}</a><br>
      - <a rel="song-country">{country}</a>
    <ol type=I>
      <li><a rel="song-part">{part_1_name}</a></li>
      <li><a rel="song-part">{part_2_name}</a></li>
                .
                .
                .
      <li><a rel="song-part">{part_N_name}</a></li>
    </ol>
  </li>
```

Note that for multiple artists and composers, textual pieces will linking them
together are not included in the above example. 

## Additional Notes

* Up to 4 Additional Artists are supported
* Up to 2 Classical Composers are supported