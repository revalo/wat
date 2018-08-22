var gulp = require('gulp');
const minify = require('gulp-minify');
 
gulp.task('minify', function() {
  gulp.src(['wat/static/*.js'])
    .pipe(minify({
        ext: {
            src: '.js',
            min: '.min.js',
        },
        noSource: true,
    }))
    .pipe(gulp.dest('wat/static'))
});
