// Bounded, exact UCUM-compatible unit subset for the regulatory proof.
// This table is shared by compiler admission and dependency-free generated code.
// It is NOT a complete UCUM parser or full QUDT ontology.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Dimension { Current, Power, Voltage, Duration, Length }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct UnitSpec {
    pub dimension: Dimension,
    pub numerator: i128,
    pub denominator: i128,
}

// The ratio converts into a canonical base (A, W, V, s, mm).
pub fn unit_spec(symbol: &str) -> Option<UnitSpec> {
    let (dimension, numerator, denominator) = match symbol {
        "A" => (Dimension::Current, 1, 1),
        "mA" => (Dimension::Current, 1, 1000),
        "kA" => (Dimension::Current, 1000, 1),
        "W" => (Dimension::Power, 1, 1),
        "kW" => (Dimension::Power, 1000, 1),
        "MW" => (Dimension::Power, 1_000_000, 1),
        "V" => (Dimension::Voltage, 1, 1),
        "kV" => (Dimension::Voltage, 1000, 1),
        "s" => (Dimension::Duration, 1, 1),
        "min" => (Dimension::Duration, 60, 1),
        "h" => (Dimension::Duration, 3600, 1),
        "mm" => (Dimension::Length, 1, 1),
        "cm" => (Dimension::Length, 10, 1),
        "m" => (Dimension::Length, 1000, 1),
        "[in_i]" => (Dimension::Length, 127, 5),
        "[ft_i]" => (Dimension::Length, 1524, 5),
        _ => return None,
    };
    Some(UnitSpec { dimension, numerator, denominator })
}
