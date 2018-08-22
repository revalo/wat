var debouncer;

var viewer = new Vue({
    el: '#viewer',
    data: {
        query: '',
        err: '',
        nores: false,
        results: [],
        searchby: 'user',
        loading: false,
    },
    watch: {
        searchby: function(newVal, oldVal) {
            this.doSearch();
        },
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
                this.loading = false;
            });
        },
        doSearch: function() {
            this.err = "";
            this.nores = false;
            this.loading = true;

            if (this.query.length >= 1)
            axios.get('/api/classes/search/' + this.query + '/by/' + this.searchby).then((response) => {
                this.loading = false;
                if (response.data.error != null) {
                    this.results = [];
                    this.err = "DONE";
                } else {
                    this.err = "";
                    this.nores = false;
                    this.results = response.data;

                    if (this.results.length == 0) {
                        this.nores = true;
                    }
                }
            })
            else
            this.loadCommon();
        },
        debounceSearch: function() {
            clearTimeout(debouncer);
            this.err = "";
            this.nores = false;
            this.loading = true;
            debouncer = setTimeout(this.doSearch, 800);
        },
    },
    beforeMount: function() {
        this.loadCommon();
    },
})
