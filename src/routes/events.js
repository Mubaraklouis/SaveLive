const express = require("express");
const router = express.Router();
const { query } = require("../config/db");

// GET all events (with optional pagination and filters)
router.get("/", async (req, res) => {
  try {
    const page = parseInt(req.query.page, 10) || 1;
    const pageSize = parseInt(req.query.page_size, 10) || 50;
    const offset = (page - 1) * pageSize;

    // Optional filters
    const { event_type, admin1, country, year } = req.query;
    let whereClause = "";
    const params = [];
    const conditions = [];

    if (event_type) {
      params.push(event_type);
      conditions.push(`event_type = $${params.length}`);
    }
    if (admin1) {
      params.push(admin1);
      conditions.push(`admin1 = $${params.length}`);
    }
    if (country) {
      params.push(country);
      conditions.push(`country = $${params.length}`);
    }
    if (year) {
      params.push(parseInt(year, 10));
      conditions.push(`year = $${params.length}`);
    }

    if (conditions.length > 0) {
      whereClause = "WHERE " + conditions.join(" AND ");
    }

    // Get total count
    const countResult = await query(
      `SELECT COUNT(*) FROM events ${whereClause}`,
      params
    );
    const total = parseInt(countResult.rows[0].count, 10);

    // Get paginated results
    const dataParams = [...params, pageSize, offset];
    const result = await query(
      `SELECT * FROM events ${whereClause} ORDER BY event_date DESC LIMIT $${dataParams.length - 1} OFFSET $${dataParams.length}`,
      dataParams
    );

    res.json({
      total,
      page,
      page_size: pageSize,
      data: result.rows,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET single event by id
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query("SELECT * FROM events WHERE id = $1", [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Event not found" });
    }
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST create a new event
router.post("/", async (req, res) => {
  try {
    const {
      event_id_cnty, event_date, year, time_precision, disorder_type,
      event_type, sub_event_type, actor1, assoc_actor_1, inter1,
      actor2, assoc_actor_2, inter2, interaction, civilian_targeting,
      iso, region, country, admin1, admin2, admin3, location,
      latitude, longitude, geo_precision, source, source_scale,
      notes, fatalities, tags, timestamp,
    } = req.body;

    if (!event_id_cnty || !event_date || !year) {
      return res.status(400).json({
        error: "event_id_cnty, event_date, and year are required",
      });
    }

    const result = await query(
      `INSERT INTO events (
        event_id_cnty, event_date, year, time_precision, disorder_type,
        event_type, sub_event_type, actor1, assoc_actor_1, inter1,
        actor2, assoc_actor_2, inter2, interaction, civilian_targeting,
        iso, region, country, admin1, admin2, admin3, location,
        latitude, longitude, geo_precision, source, source_scale,
        notes, fatalities, tags, timestamp
      ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, $31
      ) RETURNING *`,
      [
        event_id_cnty, event_date, year, time_precision, disorder_type,
        event_type, sub_event_type, actor1, assoc_actor_1, inter1,
        actor2, assoc_actor_2, inter2, interaction, civilian_targeting,
        iso, region, country, admin1, admin2, admin3, location,
        latitude, longitude, geo_precision, source, source_scale,
        notes, fatalities, tags, timestamp,
      ]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    if (err.code === "23505") {
      return res.status(409).json({ error: "Event with this event_id_cnty already exists" });
    }
    res.status(500).json({ error: err.message });
  }
});

// DELETE an event
router.delete("/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const result = await query("DELETE FROM events WHERE id = $1 RETURNING *", [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Event not found" });
    }
    res.json({ message: "Event deleted", event: result.rows[0] });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
