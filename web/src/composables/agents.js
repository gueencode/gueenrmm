
import { ref } from "vue"
import { fetchAgents } from "@/api/agents"
import { formatAgentOptions } from "@/utils/format"

// agent dropdown
export function useAgentDropdown() {
  const agent = ref(null)
  const agents = ref([])
  const agentOptions = ref([])

  // specifing flat returns an array of hostnames versus {value:id, label: hostname}
  async function getAgentOptions(flat = false) {
    agentOptions.value = formatAgentOptions(await fetchAgents({ detail: false }), flat)
  }

  return {
    //data
    agent,
    agents,
    agentOptions,

    //methods
    getAgentOptions
  }
}
