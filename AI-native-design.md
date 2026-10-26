# AI-native systemdesign för stora system

En central utmaning när AI används för att utveckla större system är att kvaliteten tenderar att försämras när mängden sammanhang växer. Även om modellen tekniskt kan hantera stora kontextfönster blir förståelsen mindre precis vad gäller kravtolkning, arkitekturdisciplin, konsekvens mellan komponenter och spårbarhet.

## Layering som kontextbegränsning

Arkitekturen bör delas upp i lager där varje lager endast känner till relevanta kontrakt mot angränsande lager.

```text
UI
↓
Application
↓
Domain
↓
Infrastructure
```

AI behöver då förstå en begränsad del av systemet åt gången istället för hela kodbasen.

## Komponenter som självständiga enheter

Varje komponent bör beskrivas explicit:

```yaml
Component: CustomerManagement

Responsibilities:
  - Manage customer lifecycle

Inputs:
  - CreateCustomerRequest

Outputs:
  - CustomerCreatedEvent

Dependencies:
  - CustomerRepository

Constraints:
  - Email must be unique
```

Komponenten blir därmed ett avgränsat sammanhang som kan utvecklas och verifieras isolerat.

## Krav → Test → Kod

Istället för:

```text
Krav
↓
Kod
```

bör processen vara:

```text
Krav
↓
Acceptanskriterier
↓
Tester
↓
Kod
```

Tester blir då komponentens exekverbara specifikation.

## Kontrakt över implementation

Det viktigaste att beskriva är inte hur komponenten är implementerad utan vilket kontrakt den erbjuder.

```yaml
Preconditions:
  Email unique

Postconditions:
  Customer exists
  Status=Active

Failure cases:
  DuplicateEmailException
```

Så länge kontraktet hålls kan implementationen förändras utan att resten av systemet påverkas.

## Explicit datautbyte

Datamodeller ska vara tydliga och formella.

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "status": "ACTIVE"
}
```

Det minskar risken för feltolkningar och påhittade attribut.

## Arkitektur som graf

AI arbetar ofta bättre med explicita beroenden än med långa arkitekturdokument.

```text
UI
 ↓
Customer API
 ↓
Customer Domain
 ↓
Repository

Customer Domain
 ↓
Event Publisher
 ↓
Kafka
```

Det gör det tydligt vilka beroenden som är tillåtna.

---

# Tester som komplett kontrakt

För AI-utvecklade system räcker det inte med funktionella tester. Redan från början bör komponentens fullständiga beteende beskrivas och verifieras.

## Funktionella krav

```text
✓ kund kan skapas
✓ e-post måste vara unik
```

## Affärssemantik

```text
✓ ACTIVE innebär att kunden får handla
✓ BLOCKED innebär att köp nekas
```

## API-kontrakt

```text
✓ korrekta HTTP-statuskoder
✓ följer API-guidelines
✓ korrekt versionshantering
```

## Nätverksrepresentation

```text
✓ korrekt JSON-struktur
✓ inga cirkulära referenser
✓ payloadgränser uppfylls
```

## Samtidighet

```text
✓ dubbla skapaförsök ger exakt en kund
✓ race conditions hanteras korrekt
```

## Prestanda

```text
✓ p95 < 100 ms
✓ p99 < 250 ms
```

## Kapacitet och volym

```text
✓ 1000 requests/s
✓ definierad datavolym stöds
```

## Robusthet

```text
✓ timeout-hantering
✓ degradering vid fel i beroenden
```

## Observability

```text
✓ korrelations-ID
✓ metrics
✓ loggstandarder
✓ tracing
```

---

# Testsviten som exekverbar specifikation

I ett AI-optimerat arbetssätt är det inte koden som är den primära sanningskällan.

Den primära artefakten är:

```text
Kompontens förmågor
↓
Kontrakt
↓
Datamodell
↓
Tester
↓
Kod
```

AI får då uppgiften:

> Här är komponentens kontrakt och tester. Implementera valfri lösning som uppfyller samtliga krav.

På så sätt begränsas frihetsgraderna samtidigt som implementationen kan utvecklas och ersättas.

---

# Ny arkitekturprincip: Context Budget

En möjlig framtida arkitekturprincip är att varje komponent ska vara tillräckligt liten för att kunna förstås, verifieras och modifieras isolerat av både människor och AI.

Man kan formulera det som:

> En komponent ska kunna beskrivas fullständigt genom ansvar, kontrakt, datamodell och verifieringskrav inom en begränsad och hanterbar kontext.

---

# Sammanfattning

AI-vänliga system kännetecknas av:

1. Små och självständiga komponenter.
2. Tydliga kontrakt mellan komponenter.
3. Explicit datamodell och datautbyte.
4. Full spårbarhet från krav till tester och kod.
5. Begränsade och tydliga beroenden.
6. Layering som reducerar kontextstorleken.
7. Tester som täcker hela spektrumet:
   - affärslogik
   - semantik
   - API-kontrakt
   - nätverksrepresentation
   - samtidighet
   - prestanda
   - kapacitet
   - robusthet
   - observability

I denna modell blir koden i stor utsträckning en implementation av en redan definierad och verifierbar specifikation. Det verkliga värdet ligger i de formella kontrakten och testerna som beskriver vad systemet ska göra och bevisar att det gör det korrekt.
