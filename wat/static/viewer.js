var debouncer;

var viewer = new Vue({
    el: '#viewer',
    data: {
        query: '',
        err: '',
        nores: false,
        page: 0,
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
        loadCommon: function(fresh = true) {
            if (fresh) this.page = 0;
            axios.get('/api/classes/common?page=' + this.page).then((response) => {
                if (fresh)
                    this.results = response.data;
                else
                    this.results.push(...response.data);

                this.loading = false;
            });
        },
        doSearch: function(fresh = true) {
            this.err = "";
            this.nores = false;
            this.loading = true;
            if (fresh) this.page = 0;

            if (this.query.length >= 1)
            axios.get('/api/classes/search/' + this.query +
                      '/by/' + this.searchby +
                      '?page=' + this.page).then((response) => {
                this.loading = false;
                if (response.data.error != null) {
                    this.results = [];
                    this.err = "DONE";
                } else {
                    this.err = "";
                    this.nores = false;

                    if (fresh)
                        this.results = response.data;
                    else
                        this.results.push(...response.data);

                    if (this.results.length == 0) {
                        this.nores = true;
                    }
                }
            })
            else
            this.loadCommon(fresh);
        },
        debounceSearch: function() {
            clearTimeout(debouncer);
            this.err = "";
            this.nores = false;
            this.loading = true;
            debouncer = setTimeout(this.doSearch, 800);
        },
        loadMore: function() {
            this.page++;
            this.doSearch(false);
        },
    },
    beforeMount: function() {
        this.loadCommon();
    },
})
