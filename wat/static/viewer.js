var debouncer;

var viewer = new Vue({
    el: '#viewer',
    data: {
        query: '',
        results: [],
    },
    computed: {
        rowCount: function() {     
            return Math.ceil(this.results.length / 2);
        },  
    },
    methods: {
        itemCountInRow: function(index) {
            return this.results.slice((index - 1) * 2, index * 2)
        },
        loadCommon: function() {
            axios.get('/api/classes/common').then((response) => {
                this.results = response.data;
            });
        },
        doSearch: function() {
            if (this.query.length >= 1)
            axios.get('/api/classes/search/' + this.query).then((response) => {
                this.results = response.data;
            });
            else
            this.loadCommon();
        },
        debounceSearch: function() {
            clearTimeout(debouncer);
            debouncer = setTimeout(this.doSearch, 800);
        },
    },
    beforeMount: function() {
        this.loadCommon();
    },
})
