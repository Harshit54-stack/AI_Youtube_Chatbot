import { askQuestion, checkHealth } from './src/services/api.js'

async function test() {
  try {
    const health = await checkHealth()
    console.log("Health:", health)
  } catch(e) {
    console.log("Health Error:", e)
  }
  try {
    const res = await askQuestion("https://www.youtube.com/watch?v=iVDuUI-k1fE", "Summary?")
    console.log("Success:", res)
  } catch(e) {
    console.log("Caught Error:", e)
  }
}
test()
