extends Node

class_name DeliverySystem

var delivered_parcels: Array[String] = []

func deliver(parcel_id: String, dock_id: String) -> bool:
	if parcel_id.is_empty() or dock_id.is_empty():
		return false
	delivered_parcels.append(parcel_id + "@" + dock_id)
	return true
