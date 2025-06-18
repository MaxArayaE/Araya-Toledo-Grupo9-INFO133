CREATE TABLE "Clientes" (
  "Id_cliente" int PRIMARY KEY,
  "Nombre_cliente" text,
  "Telefono_cliente" varchar,
  "Correo_cliente" text
);

CREATE TABLE "Mesas" (
  "N_Mesa" int PRIMARY KEY,
  "Capacidad" int,
  "Ubicacion" int
);

CREATE TABLE "Reservas" (
  "Id_reserva" int PRIMARY KEY,
  "Id_cliente" int,
  "Id_mesa" int,
  "Id_estado" int,
  "Fecha" date,
  "Cantidad_personas" int
);

CREATE TABLE "Platillos" (
  "Id_platillo" int PRIMARY KEY,
  "Nombre" varchar,
  "Precio" int,
  "Descripcion" text
);

CREATE TABLE "Pedidos" (
  "Id_pedido" int PRIMARY KEY,
  "Id_venta" int,
  "Id_mesa" int,
  "Id_platillo" int,
  "Cantidad_platillo" int,
  "Subtotal" int
);

CREATE TABLE "Ventas" (
  "Id_ventas" int PRIMARY KEY,
  "Id_metodo" int,
  "Id_garzon" int,
  "Fecha" date,
  "Propina" int,
  "Total_venta" int
);

CREATE TABLE "MetodoPago" (
  "Id_metodo" int PRIMARY KEY,
  "Metodo" varchar
);

CREATE TABLE "EstadoReserva" (
  "Id_estado" int PRIMARY KEY,
  "Estado" varchar
);

CREATE TABLE "Ubicaciones" (
  "Id_ubicacion" int PRIMARY KEY,
  "Ubicacion_local" varchar
);

CREATE TABLE "Garzones" (
  "Id_garzon" int PRIMARY KEY,
  "Nombre_garzon" text,
  "Telefono_garzon" varchar,
  "Correo_garzon" text
);

ALTER TABLE "Mesas"
  ADD FOREIGN KEY ("Ubicacion") REFERENCES "Ubicaciones" ("Id_ubicacion");

ALTER TABLE "Reservas"
  ADD FOREIGN KEY ("Id_cliente") REFERENCES "Clientes" ("Id_cliente"),
  ADD FOREIGN KEY ("Id_mesa") REFERENCES "Mesas" ("N_Mesa"),
  ADD FOREIGN KEY ("Id_estado") REFERENCES "EstadoReserva" ("Id_estado");

ALTER TABLE "Pedidos"
  ADD FOREIGN KEY ("Id_venta") REFERENCES "Ventas" ("Id_ventas"),
  ADD FOREIGN KEY ("Id_mesa") REFERENCES "Mesas" ("N_Mesa"),
  ADD FOREIGN KEY ("Id_platillo") REFERENCES "Platillos" ("Id_platillo");

ALTER TABLE "Ventas"
  ADD FOREIGN KEY ("Id_metodo") REFERENCES "MetodoPago" ("Id_metodo"),
  ADD FOREIGN KEY ("Id_garzon") REFERENCES "Garzones" ("Id_garzon");
