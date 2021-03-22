/* eslint-env node */

"use strict";

const autoprefixer = require("autoprefixer");
const babel = require("gulp-babel");
const csso = require("postcss-csso");
const eslint = require("gulp-eslint");
const gulp = require("gulp");
const minify = require("gulp-babel-minify");
const plumber = require("gulp-plumber");
const postcss = require("gulp-postcss");
const postcss_scss = require("postcss-scss");
const realFavicon = require("gulp-real-favicon");
const rename = require("gulp-rename");
const reporter = require("postcss-reporter");
const sass = require("gulp-sass");
const sourcemaps = require("gulp-sourcemaps");
const stylelint = require("stylelint");
const svg_sprite = require("gulp-svg-sprite");


// #############################################################################
// SVG SPRITE

gulp.task("svg-sprite", function () {
  return gulp.src("static_src/img/svg_sprite/*.svg")
    .pipe(plumber())
    .pipe(svg_sprite({
      mode: {
        inline: true,
        symbol: {
          dest: "",
          sprite: "sprite.symbol.svg",
        },
      },
    }))
    .pipe(gulp.dest("static/img/"));
});


// #############################################################################
// JS

gulp.task("js", function () {
  return gulp.src("static_src/js/*.js")
    .pipe(plumber({
      errorHandler: function () {
        this.emit("end");
      },
    }))
    .pipe(sourcemaps.init())
    .pipe(eslint())
    .pipe(eslint.format())
    .pipe(eslint.failAfterError())
    .pipe(rename({
      suffix: ".min",
    }))
    .pipe(babel())
    .pipe(minify())
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("static/js/"));
});


// #############################################################################
// SASS

gulp.task("sass", function () {
  return gulp.src("static_src/scss/**/*.scss")
    .pipe(plumber())
    .pipe(sourcemaps.init())
    .pipe(postcss([
      stylelint(),
      reporter({
        clearReportedMessages: true,
      }),
    ], {
      syntax: postcss_scss,
    }))
    .pipe(sass().on("error", sass.logError))
    .pipe(rename({
      suffix: ".min",
    }))
    .pipe(postcss([
      autoprefixer(),
      csso(),
    ]))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("static/css/"));
});

// #############################################################################
// GENERATE FAVICON

gulp.task("generate-favicon", function (done) {
  realFavicon.generateFavicon({
    masterPicture: "static_src/img/favicons/favicon.png",
    dest: "static/img/favicons",
    iconsPath: "/static/img/favicons",
    design: {
      ios: {
        masterPicture: "static_src/img/favicons/favicon_ios.png",
        pictureAspect: "noChange",
        assets: {
          ios6AndPriorIcons: false,
          ios7AndLaterIcons: false,
          precomposedIcons: false,
          declareOnlyDefaultIcon: true,
        },
      },
      desktopBrowser: {},
      windows: {
        masterPicture: "static_src/img/favicons/favicon_windows.png",
        pictureAspect: "noChange",
        backgroundColor: "#ffffff",
        onConflict: "override",
        assets: {
          windows80Ie10Tile: false,
          windows10Ie11EdgeTiles: {
            small: false,
            medium: true,
            big: false,
            rectangle: false,
          },
        },
      },
      androidChrome: {
        masterPicture: "static_src/img/favicons/favicon_android.png",
        pictureAspect: "noChange",
        themeColor: "#ffffff",
        manifest: {
          name: "mal2DB",
          display: "standalone",
          orientation: "notSet",
          onConflict: "override",
          declared: true,
        },
        assets: {
          legacyIcon: false,
          lowResolutionIcons: false,
        },
      },
    },
    settings: {
      masterPicture: "static_src/img/favicons/favicon_safari.svg",
      scalingAlgorithm: "Mitchell",
      errorOnImageTooSmall: false,
      readmeFile: false,
      htmlCodeFile: false,
      usePathAsIs: false,
    },
    markupFile: "static_src/img/favicons/faviconData.json",
  }, function () {
    done();
  });
});


// #############################################################################
// TASK

exports.default = function() {
  gulp.watch("static_src/img/svg_sprite/*.svg", gulp.series("svg-sprite"));
  gulp.watch("static_src/js/*.js", gulp.series("js"));
  gulp.watch("static_src/scss/**/*.scss", gulp.series("sass"));
};
