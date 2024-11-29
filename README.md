<!-- define height and width -->

<img src="docs/assets/image.png" alt="fastbruno" width="200">

# Welcome to Fast Bruno

Fast Bruno is a tool that allows you to generate Bruno files from FastAPI apps. What if you could generate a bunch of Bruno files from your FastAPI app and have them automatically updated when you make changes to your app?

Fast Bruno allows you to do just that saving you a lot of time writing repetitive API routes and queries.


## Install

```bash
pip install fastbruno
```

## Usage

fastbruno is very simple to use. Just give it the path to your FastAPI app, just like you would do with `uvicorn` or `fastapi run`.

```bash
# fastbruno <path_to_your_fastapi_app>
fastbruno "app.main:app"
```

And Boom! This will generate a `bruno` directory in the root of your project containing all the Bruno files for your API routes.
Now open your Bruno app and open the `bruno` folder and you should see all your favorite API routes and queries.

# Report an issue
- [Give it a star ⭐️](https://github.com/fastbruno/fastbruno)
- [Report an issue](https://github.com/fastbruno/fastbruno/issues)
