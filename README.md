# Pyrolysis Furnace Intelligence

## Combustion Workbench

I built this project to connect the combustion equations we learn as engineers with the way a real industrial furnace behaves.

Combustion looks simple on paper:

\[
\text{Fuel} + \text{Oxygen} \rightarrow \text{Products} + \text{Heat}
\]

But in an industrial furnace, changing one variable can affect many others. Fuel composition changes heating value, density, Wobbe index, oxygen demand and emissions. Excess air changes flue-gas flow and stack losses. Firing changes burner loading and heat transfer. Process load changes how much heat the furnace must supply.

The purpose of this workbench is simple:

> **Change one combustion or furnace parameter and immediately see what else changes, how much it changes, and why.**

The public model uses generalised teaching conditions. It is not a plant digital twin, burner-design package, CFD model, BMS, APC replacement or safety system.

---

## Why combustion optimisation matters

Fired equipment sits at the heart of many energy-intensive industries.

Pyrolysis furnaces supply the heat required to crack hydrocarbons into olefins. Cement kilns provide the thermal environment needed to form clinker. Furnaces and reheaters are central to steel production. Fired heaters and boilers are used throughout refining, petrochemical and power-generation processes.

These plants operate at very large production rates, so even a small improvement in furnace efficiency can mean a significant reduction in fuel consumption.

But optimisation is not only about reducing fuel.

A change in firing can also affect:

- CO₂ emissions;
- flue-gas losses;
- excess oxygen;
- heat distribution;
- burner loading;
- tube temperature;
- coking tendency;
- furnace run length;
- process stability.

So the real objective is not simply **use less fuel**.

The objective is:

> **Supply the heat required by the process, distribute it correctly, and lose as little energy as possible while staying within the thermal and operating limits of the furnace.**

This is the engineering problem I wanted to explore.

---

## The furnace as one connected system

A fired furnace can be simplified as:

\[
\text{Fuel + Air}
\rightarrow
\text{Combustion}
\rightarrow
\text{Heat release}
\rightarrow
\text{Radiation + Convection}
\rightarrow
\text{Process}
\]

But the variables are coupled.

For example:

\[
\text{Fuel composition}
\rightarrow
LHV,\;MW,\;Wobbe
\rightarrow
\text{Fuel flow}
\rightarrow
\text{Oxygen demand}
\rightarrow
\text{Air flow}
\rightarrow
\text{Flue gas}
\rightarrow
\text{CO}_2
\]

The software is built around these relationships rather than around isolated calculations.

![Conceptual industrial pyrolysis furnace](assets/furnace.svg)

*Conceptual furnace architecture used in this project. The figure is independently drawn for the public workbench and is not a vendor P&ID or a plant drawing.*

---

## 1. Fuel composition

A furnace controller may measure fuel flow, but the same mass or volume of two gases does not necessarily release the same amount of heat.

Hydrogen, methane, ethane, ethylene, propane and carbon monoxide have different:

- molecular weights;
- lower heating values;
- densities;
- stoichiometric oxygen requirements;
- carbon contents;
- burner interchangeability behaviour.

For a mixture:

\[
MW_{fuel}=\sum_i x_i MW_i
\]

where \(x_i\) is the mole fraction of each component.

The workbench supports:

\[
H_2,\ CH_4,\ C_2H_4,\ C_2H_6,\ C_3H_8,\ CO,\ CO_2,\ N_2
\]

Fuel composition is always closed to 100%. When I change one component, I can select another component to act as the balance.

That makes it possible to study questions such as:

- What happens when hydrogen increases and methane decreases?
- What happens when a fuel becomes more hydrocarbon-rich?
- What happens to fuel flow if the process still needs the same fired duty?

---

## 2. Lower Heating Value

For fixed fuel composition, chemical heat release is approximately:

\[
Q_{fired}=\dot m_{fuel}\,LHV
\]

Therefore, if the process heat requirement stays constant:

\[
\boxed{
\dot m_{fuel}=\frac{Q_{required}}{LHV}
}
\]

This is one reason fuel flow alone is not enough to describe furnace firing.

If fuel quality changes, the controller may need a different mass flow to provide the same heat input.

The workbench calculates the mass-based LHV from the declared mixture and then shows the effect on required fuel flow.

---

## 3. Wobbe Index

LHV per kilogram is not the whole story for a gaseous burner.

Gas density also changes.

A useful fuel-interchangeability parameter is the Wobbe Index:

\[
\boxed{
WI=\frac{HV_v}{\sqrt{SG}}
}
\]

where:

- \(HV_v\) is heating value per normal volume;
- \(SG\) is gas specific gravity relative to air.

This matters because a burner operating with a similar pressure difference does not respond only to mass LHV.

The workbench therefore shows both:

\[
\boxed{LHV}
\qquad\text{and}\qquad
\boxed{Wobbe\ Index}
\]

This is especially useful when comparing hydrogen-rich and methane-rich gases.

---

## 4. Stoichiometric oxygen and air

For a generic fuel containing carbon, hydrogen and oxygen, the theoretical oxygen requirement can be written as:

\[
\boxed{
n_{O_2,st}=C+\frac{H}{4}-\frac{O}{2}
}
\]

For example:

\[
CH_4+2O_2\rightarrow CO_2+2H_2O
\]

and:

\[
H_2+\frac{1}{2}O_2\rightarrow H_2O
\]

The workbench calculates the oxygen requirement from the elemental balance of the full fuel mixture.

From this it calculates:

- stoichiometric air;
- actual combustion air;
- dry and wet flue-gas composition;
- flue-gas mass flow.

The public model also includes the effect of humid ambient air in the combustion balance.

---

## 5. Excess air

Industrial furnaces normally operate with air above the theoretical minimum.

\[
Air_{actual}=Air_{stoich}(1+EA)
\]

where \(EA\) is the excess-air fraction.

Too little air can lead toward incomplete combustion.

Too much air is also undesirable because additional air has to be heated and finally leaves with the flue gas.

Conceptually:

\[
EA\uparrow
\rightarrow
Air\ flow\uparrow
\rightarrow
Flue\ gas\ flow\uparrow
\rightarrow
Stack\ heat\ loss\uparrow
\]

This makes excess air an optimisation variable, not simply an analyser number.

A particularly important point is the difference between **CO₂ mass flow** and **CO₂ concentration**.

If fuel flow and fuel composition are unchanged:

\[
EA\uparrow
\]

does not create more carbon.

So the CO₂ formed by combustion remains approximately unchanged, while the additional air dilutes it:

\[
CO_2\;vol\%\downarrow
\]

The software shows this relationship directly.

---

## 6. Draft and combustion air

In an induced-draft furnace, the ID fan maintains the furnace slightly below atmospheric pressure.

The physical relationship is:

\[
ID\ fan
\rightarrow
Furnace\ draft
\rightarrow
Burner\ \Delta P
\rightarrow
Air\ drawn\ through\ burners
\]

This is one of the most important links between combustion and furnace control.

However, an exact numerical relationship between draft and burner air flow needs burner resistance, register position, leakage information and fan/system curves.

I therefore do **not** force a false plant-calibrated draft-to-airflow equation into this public model.

The workbench treats excess air quantitatively and keeps draft as an engineering/control concept until enough information exists for a defensible numerical model.

---

## 7. Heat transfer and why firing alone is not enough

A furnace is useful only if the heat released by combustion reaches the process.

Inside the firebox, radiation is strongly dependent on temperature:

\[
Q_{rad}\propto
\varepsilon\sigma A\left(T_g^4-T_t^4\right)
\]

This fourth-power relationship is one reason local furnace temperature and flame behaviour matter so much.

Total fired duty is also not enough to describe a furnace.

Two furnaces can have the same total firing but different heat distributions.

A local high-flux region can increase tube-metal temperature even if the average furnace duty looks acceptable.

In a pyrolysis furnace this becomes particularly important because coke progressively adds resistance between the hot tube wall and the reacting gas.

As coking develops, more tube-metal temperature may be required to transfer the same process heat.

That is why combustion optimisation connects directly with:

\[
\text{Heat flux}
\rightarrow
\text{Tube temperature}
\rightarrow
\text{Coking}
\rightarrow
\text{Run length}
\]

The current public combustion workbench does not claim to predict local tube-metal temperature or coking rate. Those belong to a later heat-transfer/process layer.

---

## 8. Why a pyrolysis furnace is different from a simple heater

A cracking furnace does not only provide sensible heat.

The feed and dilution steam have to be heated, but the hydrocarbon also undergoes strongly endothermic chemical reactions.

So the process heat requirement contains both:

\[
\boxed{\text{Sensible heat}}
\]

and:

\[
\boxed{\text{Reaction heat}}
\]

For the public workbench I use a simple source-informed engineering load model:

\[
L=
\dot m_{HC}
+
k_s\dot m_{steam}
\]

with a separate weighting for dilution steam.

The required furnace duty is then scaled from a generalised start-of-run or end-of-run teaching condition:

\[
\boxed{
Q_{required}
=
Q_{ref}\frac{L}{L_{ref}}
}
\]

This is intentionally a first engineering approximation rather than a rigorous cracking-kinetics model.

At low feed rates, residence time, steam requirement and target cracking severity no longer behave like a simple linear scaling. The workbench therefore warns when the user moves into the low-load range instead of pretending that the normal-load model remains exact.

---

## 9. Burner loading and firing distribution

The same total furnace duty can be distributed differently.

For a simple bottom/sidewall split:

\[
Q_{bottom}=f_bQ_{fired}
\]

\[
Q_{sidewall}=(1-f_b)Q_{fired}
\]

and average burner loading is calculated from the active burner-group count.

This makes it possible to see immediately how changing firing distribution affects each burner group while total furnace duty remains conserved.

The public burner counts and loading limits are generalised teaching values rather than reproduced vendor data.

---

## 10. Combustion and process control

Understanding the combustion physics becomes even more important when designing the control system.

A furnace has significant thermal mass.

The refractory and tubes store heat, so coil outlet temperature does not respond instantly when fuel firing changes.

At the same time, a feed-flow disturbance can affect the process much faster.

This is why a good furnace control structure can combine:

\[
\text{Feed-forward}
+
\text{Feedback}
\]

Feed and dilution-steam flow can indicate that heat demand is changing before the slow furnace temperature has fully responded.

The temperature controller then corrects the remaining error.

Conceptually:

\[
\text{Feed change}
\rightarrow
\text{Feed-forward fuel demand}
\rightarrow
\text{Furnace}
\rightarrow
\text{Outlet temperature}
\rightarrow
\text{Feedback correction}
\]

![Conceptual firing and control architecture](assets/control.svg)

*Conceptual control architecture independently drawn for this public project. It shows engineering relationships, not a deployed controller algorithm or proprietary control logic.*

Control design is also an optimisation problem.

If a process is poorly controlled, operators normally need larger margins from constraints.

Better control can reduce process variability:

\[
\boxed{
Better\ control
\rightarrow
Lower\ variability
\rightarrow
Smaller\ operating\ margin
\rightarrow
Better\ efficiency
}
\]

For a furnace, lower variability can mean less unnecessary overfiring, more stable thermal severity and better use of the available operating envelope.

---

## Why I built the software

I developed this project from my experience working with industrial olefin cracking furnaces and from studying the combustion, heat-transfer and control philosophy around them.

What interested me most was that variables which appear separately on a control-room screen are actually parts of one physical system.

Fuel composition, fuel flow, Wobbe index, fired duty, excess oxygen, air flow, flue-gas flow, furnace draft, burner distribution and process temperature are all connected.

I wanted a tool where I could change one of these variables and immediately see those connections.

The result is this **Combustion Workbench**.

The engineering approach is informed by my experience with real industrial cracking-furnace systems, including Technip-designed furnace architecture, but the public implementation is independently authored and uses generalised teaching conditions.

---

## How to use the workbench

The first screen is designed as one horizontal engineering workspace.

There are three main areas.

### Inputs

Change:

- hydrocarbon feed rate;
- steam/feed ratio;
- fuel composition;
- excess air;
- bottom/sidewall firing share.

For fuel-composition studies you can also choose what should remain constant:

- fired duty;
- fuel mass flow;
- burner pressure difference, using the Wobbe approximation.

### See the effect

The graph automatically follows the last variable you changed.

If you change hydrogen, the graph becomes a hydrogen-response study.

You can then see the effect on:

- CO₂;
- fuel flow;
- Wobbe Index;
- LHV;
- air flow;
- flue-gas flow;
- CO₂ intensity.

If you change excess air, the graph automatically changes to an excess-air study.

If you change feed rate, it changes to a load-response study.

The curve is recalculated using the same engineering model as the numerical results. It is not a decorative fitted line.

### Before → Now

Every change is compared with the condition immediately before it.

The workbench shows:

\[
\boxed{\text{Before}}
\rightarrow
\boxed{\text{Now}}
\rightarrow
\boxed{\text{Change}}
\]

for the main combustion quantities.

A **Why did this happen?** button opens a second layer showing the physical path and equations behind the change.

---

## What the current model calculates

The current combustion layer calculates:

- mixture molecular weight;
- mass LHV;
- volumetric LHV;
- Wobbe Index;
- required fired duty from the process-load teaching model;
- fuel mass and normal volumetric flow;
- stoichiometric oxygen;
- stoichiometric air;
- actual humid combustion air;
- wet and dry flue-gas composition;
- dry O₂;
- dry CO₂;
- flue-gas mass flow;
- CO₂ formed by combustion;
- CO₂ intensity per MWh fired;
- average, bottom and sidewall burner loading;
- low-load and burner-loading warnings.

---

## What it does not claim

The current version does not numerically predict:

- CFD flow fields;
- local flame shape;
- flame speed;
- flashback limits;
- NOx or CO emissions;
- local radiant heat flux;
- tube-metal temperature;
- tube life;
- detailed coking kinetics;
- cracking-product yield;
- calibrated ID-fan/register/leakage behaviour;
- dynamic PID trajectories;
- plant trips or safe-to-operate decisions.

Those boundaries are deliberate.

I would rather leave a quantity unavailable than display a precise-looking number without enough engineering basis.

---

## Data and confidentiality

This is a public portfolio and learning project.

The industrial experience behind it came from real furnace operation, process documentation and control philosophy, but proprietary drawings and plant-specific data are not reproduced in the public repository.

Public cases, burner counts and operating values are generalised or synthetic where necessary.

The furnace and control figures in this repository are independently drawn conceptual diagrams.

---

## Validation

The project includes automated tests for both software behaviour and engineering relationships.

The tests check, among other things, that:

- fuel compositions close to 100%;
- hydrogen-rich fuel gives lower carbon/CO₂ at constant fired duty;
- increasing excess air increases air and flue-gas flow but does not create additional carbon;
- feed and steam changes move required furnace duty in the expected direction;
- low-load conditions are flagged;
- firing redistribution conserves total duty;
- constant-fuel-flow and constant-burner-pressure studies behave according to their declared basis;
- the live response graph follows the last changed variable.

The public CI also checks that the Dash application loads successfully.

---

## Run locally

Python 3.12 is the tested CI runtime.

~~~bash
git clone https://github.com/abbasrajaei/Pyrolysis-Furnace-Intelligence.git
cd Pyrolysis-Furnace-Intelligence
python -m venv .venv
~~~

Activate the environment.

Linux/macOS:

~~~bash
source .venv/bin/activate
~~~

Windows:

~~~bat
.venv\Scripts\activate
~~~

Install:

~~~bash
python -m pip install ".[test]"
~~~

Run the workbench:

~~~bash
python app/app.py
~~~

Open:

~~~text
http://127.0.0.1:8050
~~~

---

## Repository structure

~~~text
app/        Dash combustion workbench and interface styling
src/        Combustion, furnace and supporting engineering calculations
data/       Public teaching inputs
tests/      Engineering and application tests
examples/   Example engineering calculations
docs/       Methodology, validation and model boundaries
assets/     Independently drawn public furnace and control figures
~~~

---

## Author

**Abbas Rajaei**

Chemical / Process Engineer

This project is part of my continuing work on industrial combustion, furnace optimisation, process control and decarbonisation of energy-intensive processes.
