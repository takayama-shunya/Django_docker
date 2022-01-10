const add_element = new Vue({
    el: '#add-element',
    delimiters: ["[[", "]]"],
    data: {
        inputs: [],
        names: [''],
    },
    methods: {
        addRow(index) {
            this.inputs.push('')
            console.log(index)
            this.names.push('serv_item_' + String(index + 1))
        },
        deleteRow(index) {
            this.inputs.splice(index, 1)
        },
        getName(index) {
            return 'serv_item_' + String(index)
        }
    }
})
