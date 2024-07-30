module energy_module

    implicit none
    save
    
    logical, private :: module_setup = .false.

    real(kind=8) :: U, R_m, dp

contains

    subroutine set_energy(data_file)

        implicit none

        character(len=*), optional, intent(in) :: data_file
        integer, parameter :: unit = 13
        character(len=200) :: line

        if (.not.module_setup) then

            ! Open file
            if (present(data_file)) then
                call opendatafile(unit, data_file)
            else
                call opendatafile(unit, 'energy.data')
            endif

            read(unit, *) U
            read(unit, *) R_m
            read(unit, *) dp

            close(unit)
            module_setup = .true.

        end if

    end subroutine set_energy

end module energy_module