const IST_OFFSET_MINUTES = 330;
const IST_OFFSET_MS = IST_OFFSET_MINUTES * 60 * 1000;

function toIST(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return null;
  }
  return new Date(date.getTime() + IST_OFFSET_MS);
}

export function buildKolkataDate(year, month, day, hours = 0, minutes = 0, seconds = 0) {
  const utcTimestamp = Date.UTC(year, month, day, hours, minutes, seconds);
  return new Date(utcTimestamp - IST_OFFSET_MS);
}

export function parseKolkataISODate(value) {
  if (!value || typeof value !== 'string') {
    return null;
  }
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!match) {
    return null;
  }
  const year = parseInt(match[1], 10);
  const month = parseInt(match[2], 10) - 1;
  const day = parseInt(match[3], 10);
  return buildKolkataDate(year, month, day);
}

export function formatKolkataDateForInput(date) {
  if (!date || !(date instanceof Date) || Number.isNaN(date.getTime())) {
    return '';
  }
  const istDate = toIST(date);
  const year = istDate.getUTCFullYear();
  const month = `${istDate.getUTCMonth() + 1}`.padStart(2, '0');
  const day = `${istDate.getUTCDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function getKolkataToday() {
  const now = new Date();
  const istNow = toIST(now);
  if (!istNow) {
    return null;
  }
  return buildKolkataDate(istNow.getUTCFullYear(), istNow.getUTCMonth(), istNow.getUTCDate());
}

export function getKolkataTomorrow() {
  const today = getKolkataToday();
  if (!today) {
    return null;
  }
  return addKolkataDays(today, 1);
}

export function addKolkataDays(base, days = 1) {
  if (!base || !(base instanceof Date) || Number.isNaN(base.getTime())) {
    return null;
  }
  const result = new Date(base.getTime());
  result.setUTCDate(result.getUTCDate() + days);
  return result;
}

export function getKolkataMonthKey(date) {
  const istDate = toIST(date);
  if (!istDate) {
    return '';
  }
  const year = istDate.getUTCFullYear();
  const month = `${istDate.getUTCMonth() + 1}`.padStart(2, '0');
  return `${year}-${month}`;
}

export function startOfKolkataDay(date) {
  if (!date || !(date instanceof Date) || Number.isNaN(date.getTime())) {
    return null;
  }
  const istDate = toIST(date);
  return buildKolkataDate(istDate.getUTCFullYear(), istDate.getUTCMonth(), istDate.getUTCDate());
}
