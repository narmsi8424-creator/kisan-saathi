-- Kisan Saathi AI Database Schema
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS farmers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    language TEXT DEFAULT 'hi',
    state TEXT DEFAULT 'Bihar',
    district TEXT,
    plan TEXT DEFAULT 'free',
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone TEXT NOT NULL,
    direction TEXT CHECK (direction IN ('inbound','outbound')),
    msg_type TEXT,
    content TEXT,
    intent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS disease_detections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone TEXT NOT NULL,
    disease TEXT,
    confidence NUMERIC(5,2),
    severity TEXT,
    treatment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mandi_prices (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    crop TEXT NOT NULL,
    state TEXT NOT NULL,
    min_price NUMERIC(8,2),
    max_price NUMERIC(8,2),
    modal_price NUMERIC(8,2),
    price_date DATE DEFAULT CURRENT_DATE
);