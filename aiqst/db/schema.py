from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.orm import Session, relationship

from aiqst.db.base_class import Base

convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),

    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

class Customers(Base):
    __tablename__ = "customers"
    __table_args__ = {'schema': 'source'}

    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String(100), nullable=True)
    username = Column(String(100), nullable = True)
    email = Column(String(100), nullable = False )
    date_registered = Column(DateTime(), server_default=text('now()'), nullable=False)
    #address = Column(String(100), nullable=True)
    #zip = Column(Integer, nullable = True) 

    sales = relationship("Sales", back_populates="source.customer")


class Pos_Details(Base):
    __tablename__ = "pos_details"
    __table_args__ = {'schema': 'source'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    latitude = Column(Float, nullable = False)
    longitude = Column(Float, nullable = False)
    eff_start_date = Column(DateTime(), server_default=text('now()'), nullable=False)
    eff_end_date = Column(DateTime(), server_default=text("TO_TIMESTAMP('1900-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')"), nullable=False)
    date_registered = Column(DateTime(), server_default=text('now()'), nullable=False)

    sales = relationship("Sales", back_populates="source.pos_detail")
    weather_data = relationship("Weather_Data", back_populates="source.pos_detail")

class Products(Base):
    __tablename__ = "products"
    __table_args__ = {'schema': 'source'}

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(100), nullable = False)
    name = Column(String(100), nullable=True)
    qty = Column(Integer, nullable = False)
    date_registered = Column(DateTime(), server_default=text('now()'), nullable=False)
    #unit_price = Column(Float, nullable = False)

    #sales = relationship("Sales", back_populates="product")
    

class Sales(Base):
    __tablename__ = "sales"
    __table_args__ = {'schema': 'source'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable = False)
    customer_id = Column(Integer, ForeignKey('source.customers.id'), nullable = False)
    pos_id = Column(Integer, ForeignKey('source.pos_details.id'), nullable = False)
    price = Column(Float, nullable = False)
    qty = Column(Integer,  nullable = False)
    order_date = Column(Date, nullable = False)
    date_registered = Column(DateTime(), server_default=text('now()'), nullable=False)

    customer = relationship("Customers", back_populates="source.sales")
    pos_detail = relationship("Pos_Details", back_populates="source.sales")



class Weather_Data(Base):
    __tablename__ = "weather_data"
    __table_args__ = {'schema': 'source'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pos_id = Column(Integer, ForeignKey('source.pos_details.id'), nullable=False)
    weather = Column(String(100), nullable = True)
    weather_des = Column(String(100), nullable = True)
    temp = Column(Float, nullable = True)
    temp_feels_like = Column(Float, nullable = True)
    temp_min = Column(Float, nullable = True)
    temp_max = Column(Float, nullable = True)
    pressure = Column(Float, nullable = True)
    humidity = Column(Float, nullable = True)
    visibility = Column(Float, nullable = True)
    wind_speed = Column(Float, nullable = True)
    wind_deg = Column(Float, nullable = True)
    dt = Column(DateTime(), nullable = True)
    date_registered = Column(DateTime(), server_default=text('now()'), nullable=False)
    
    pos_detail = relationship("Pos_Details", back_populates="source.weather_data")


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=db.bind, naming_convention=convention)