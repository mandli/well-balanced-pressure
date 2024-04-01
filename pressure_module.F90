module pressure_module

    implicit none
    save

    logical, private :: module_setup = .false.

    logical :: split_pressure = .false.

contains

    subroutine set_pressure(data_file)

        implicit none

        character(len=*), optional, intent(in) :: data_file
        integer, parameter :: unit = 13
        character(len=200) :: line

        if (.not.module_setup) then

            ! Open file
            if (present(data_file)) then
                call opendatafile(unit, data_file)
            else
                call opendatafile(unit, 'pressure.data')
            endif

            read(unit, *) split_pressure

            close(unit)
            module_setup = .true.

        end if

    end subroutine set_pressure

end module pressure_module