import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://nnwovklgbgmdoemymkyy.supabase.co';
const supabaseKey = 'sb_publishable_kJDTDsyMSbqvd1-uqAo8cQ_3n-qFzcs';

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  console.log("Connecting to Supabase Database project: nnwovklgbgmdoemymkyy...");
  try {
    const { data, error } = await supabase.from('users').select('*').limit(5);
    if (error) {
      console.log("Supabase Connection Response:", error.message);
    } else {
      console.log("Successfully connected to Supabase Database!");
      console.log("Query Results (users table):", data);
    }
  } catch (err) {
    console.error("Connection Failed:", err);
  }
}

testConnection();
