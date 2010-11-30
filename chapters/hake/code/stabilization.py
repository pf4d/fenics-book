# Python code for the assembly of the SUPG term for the mass and advection matrices
# Defining the stabilization using local Peclet number
cppcode = """class Stab : public Expression {
public:
  GenericFunction* field; double sigma;
  Stab(): Expression(3), field(0), sigma(1.0e5){}
  void eval(Array<double>& v, const Data& data) const {
    if (!field)
      error("Attach a field function.");
    double field_norm = 0.0; double tau = 0.0;
    double h = data.cell().diameter();
    field->eval(v, data);
    for (uint i = 0;i < data.x.size(); ++i)
      field_norm += v[i]*v[i];
    field_norm = sqrt(field_norm);
    double PE = 0.5*field_norm * h/sigma;
    if (PE > DOLFIN_EPS)
      tau = 1/tanh(PE)-1/PE;
    for (uint i = 0;i < data.x.size(); ++i)
      v[i] *= 0.5*h*tau/field_norm;}};
"""
stab = Expression(cppcode); stab.field = a

# Assemble the stabilization matrices
E_stab = assemble(div(a*u)*inner(stab, grad(v))*dx)
M_stab = assemble(u*inner(stab, grad(v))*dx)

# Adding them to the A and M matrices, weighted by the global tau
tau = 0.28; E.axpy(tau, E_stab, True); M.axpy(tau, M_stab,True)
