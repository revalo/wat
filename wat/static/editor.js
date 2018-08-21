var options = {
    shouldSort: true,
    threshold: 0.6,
    location: 0,
    distance: 100,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: [
      "code",
      "name"
    ]
};

var fuse = new Fuse(classes, options);

var editor = new Vue({
    el: '#editor',
    data: {
        newCourse: '',
        selectedCourses: [],
        results: [],
    },
    watch: {
        selectedCourses: function(newValue, oldValue) {
            // TODO(revalo): Maybe handle errors gracefully?
            axios.post('/api/courses', {
                courses: this.selectedCourses,
            }).then(function(response) {
                // Nothing ...
            });
        },
    },
    methods: {
        addCourse: function() {
            var results = fuse.search(this.newCourse);

            if (results.length >= 1 && this.selectedCourses.indexOf(results[0]) < 0) {
                this.selectedCourses.push(results[0]);
            }

            this.newCourse = '';
            this.results = [];
        },
        removeCourse: function(course) {
            this.selectedCourses.splice(this.selectedCourses.indexOf(course), 1);
        },
        autocomplete: function() {
            this.results = fuse.search(this.newCourse).slice(0, 10);
        },
    },
    beforeMount: function() {
        this.selectedCourses = alreadySelected;
    },
})