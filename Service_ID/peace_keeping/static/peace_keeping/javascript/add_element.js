const add_element = new Vue({
    el: '#add-element',
    delimiters: ["[[", "]]"],
    data: {
        inputs: [],
        names: {"0": 'serv_item_0',},
        count: 0,
        lastName: ''
    },
    methods: {
        addRow() {
            this.inputs.push('')
            this.count += 1
            this.names[(String.count)] = 'serv_item_' + String(this.count)
            this.getLastName()
        },
        deleteRow(index) {
            this.inputs.splice(index, 1)
        },
        getLastName() {
            this.lastName = this.names[this.names.length - 1]
            console.log(this.lastName)
        }
    }
})
