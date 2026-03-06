const { Pool } = require("pg");

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT, 10) || 5432,
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "postgres",
  database: process.env.DB_NAME || "savelife",
});

const connectDB = async () => {
  let retries = 5;
  while (retries > 0) {
    try {
      const client = await pool.connect();
      console.log("✅ Connected to PostgreSQL database");
      client.release();
      return;
    } catch (err) {
      retries -= 1;
      console.log(
        `⏳ Waiting for database... retries left: ${retries}`
      );
      await new Promise((res) => setTimeout(res, 3000));
    }
  }
  throw new Error("Unable to connect to PostgreSQL after multiple retries");
};

const query = (text, params) => pool.query(text, params);

module.exports = { pool, connectDB, query };
