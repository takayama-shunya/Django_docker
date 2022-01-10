var fuzzy_search = new Vue({
    delimiters: ["[[", "]]"],
    el: '#fuzzy-search',
    data: {
        serv_name_or_needs: '',
        area_name: '',
        candidates: [],
        errored: false,
        loading: false,
        base_url: '',
        is_active: false,
        is_mounted: false
    },
    methods: {
        getCandidates: function () {
            const url = this.base_url + '/peace_keeping/fuzzy_search' + '/' + this.area_name + '/' + this.serv_name_or_needs
            console.log(url)
            axios.get(url)
                .then(response => {
                    const res = response.data
                    this.candidates = res.split(',')
                    console.log('[this.candidates] ', this.candidates)
                })
                .catch(error => {
                    this.candidates = []
                })
        },
        select: function (event) {
            console.log(event.currentTarget.value)
            this.$refs.input.value = event.currentTarget.value
        },
    },
    mounted() {
        console.log('[this.$refs.area_name]', this.$refs.area_name)
        this.area_name = this.$refs.area_name.value
        this.base_url = this.$refs.base_url.value
        console.log(this.area_name)
        console.log(this.base_url)
    },
    updated() {
        this.is_mounted = true
    },
});
