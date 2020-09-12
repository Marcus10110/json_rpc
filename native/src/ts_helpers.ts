export type Map<TKey, TValue> = TKey extends number
  ? { [key: number]: TValue }
  : TKey extends string
  ? { [key: string]: TValue }
  : (TKey & TValue)[];

export type AnalogValue = number;
