import { reactive, computed } from 'vue'
import { initDefaultStoreMethods } from './DefaultStore.js'

let state = reactive({
    items: {},
    order: [],
    isLoading: false
})

const { actions } = initDefaultStoreMethods(state)

export default {
    actions: {
        fetchSearchResult: actions.fetchResourceList,
    },
    results: computed(() => state.order.map(id => state.items[id])),
    isLoading: computed(() => state.isLoading)
}
