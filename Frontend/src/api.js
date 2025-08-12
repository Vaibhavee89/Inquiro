import axios from 'axios';
const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000' });
export async function search(query, max_results=5){
  const res = await API.post('/search', { query, max_results });
  return res.data;
}